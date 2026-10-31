# Tasks 116 -- The walk reads the reworded founder screens of keel-web 149 and 150

Branch `116-the-walk-reads-the-reworded-founder-screens` (worktree `wt/keel-e2e-eval-116`, `.git` a file, its own
`make venv`), off master `f893808` (4,718 passed / 0 failed / 0 errors / 53 skipped, as 109 recorded it and as this
worktree read it before any change). Built by Claude on 2026-10-31 (finished 02:24 EDT). Read only: keel-web master
`7a3105f` (149 merged: `specs/149-.../tasks.md`, *What keel-e2e-eval must read*; `ListQuestion.tsx` `ChooseList`,
`founderLists.ts` `chooseOrder` / `optionBelief` / `buyerPayerHolds` / `toListAnswer` / `lowerFirst`, `translate.ts`
`LIST_CHOOSE_PROMPT` / `buyerPayerBar`); keel-web branch `origin/150-current-solution-asks-twice` at `34740c1` (150
**NOT merged** into keel-web master when this build ended -- see FR-2); keel-cloud-docs `ab5b15ef`. **No stack, no
model, no walk, no paid call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `49da978` | FR-1 / FR-2: the page object (`harness/vectors_screens.py`) -- `list_choose`, `list_answer`, the helpers |
| `70f74a2` | FR-1 / FR-2: the calibrate leg (`evals/corpus_scenario.py`) -- `choose_faults`, `answer_boxes_faults`, one step |
| `33e4e9d` | FR-1 / FR-2: the founder screens of record (`evals/backtest.py`) |
| `9fe38da` | FR-4: `tests/test_reworded_founder_screens_116.py` (23) |
| the docs commit | this file and `AGENTS.md`'s spec-116 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `f893808` (this worktree, before any change), keel-cloud-docs `ab5b15ef`, keel-web `7a3105f` | 4,718 | 0 | 0 | 53 |
| **branch at `9fe38da` (the last code; the docs commit adds none), the same siblings** | **4,741** | **0** | **0** | **53** |

+23 tests, all `tests/test_reworded_founder_screens_116.py`. The 53 skipped are master's 53 (109's tasks.md). No failure
came from another spec.

## FR-1 Buyer and payer's Choose (keel-web 149) -- `49da978`, `70f74a2`

- [x] T001 **The pick is by label; the served index comes off the wire.** `Corridor.list_choose` still clicks
  `get_by_role("radio", name=label, exact=True)` (spec 104; 149 keeps the radio's name the row's label alone) and now
  records `label`, `drawn_index` (the label's position in `options`, the drawn order) and `served_index` -- the
  `pickedIndex` of the dimension's answer in the `PUT calibration/{vector}` the primary sent (`writes`, kept by
  `_keeping("PUT", CALIBRATION_PUT)` around `_press_primary`; `served_picked_index` reads the last 2xx write, a 409's
  second press included). `options` is unchanged as a record (the radios' words in drawn order): on Buyer and payer
  it now reads the roles then *Nobody else* LAST, so no reader may take an index from it.
- [x] T002 **The row the label was found at.** `leg_calibrate` keeps `_choose_label`'s second value (`label, row`, was
  `label, _`) on the Choose screen (`seen[-1]["row"]`): the drafted row on a live walk, the entry's typed index on the
  golden walk (the scripted list is the entry's own, so the two agree). `choose_faults` holds `served_index == row`.
- [x] T003 **The title** `seen["prompt"]` (`.listcheck__title`) is held to *Which one do you want to test?*
  (`vs_screens.BUYER_PAYER_CHOOSE_PROMPT`) on Buyer and payer; other dimensions' titles are not held (149 moved none).
- [x] T004 **The recall line and the beliefs** are read: `seen["recall"]` (`[data-testid=choose-recall]`, whitespace
  folded) and `seen["beliefs"]` (every `[data-testid=choose-belief]`, drawn order). Held: where roles are drawn, the
  recall ends *Who else has to agree: {roles}, from your last answer.* (the roles as the radios draw them); one belief
  per radio. The *Who decides* half is not held to a decider (it is the persona step's words, and absent where none
  is stored -- 149's J-4).
- [x] T005 **The bar's three cases** (`vs_screens.buyer_payer_bar`, 149's `buyerPayerBar` as a pattern): *Holds if at
  least 2 in 3 [{deciders}] say {who} had to agree the last time[ they bought {offer}].* -> `unpicked` (*the one you
  pick*), `nobody` (*nobody else*), `role` (the role in a sentence, `role_in_sentence` = 149's `lowerFirst`), with the
  deciders and the offer read where drawn. Held: `test_before["bar"]` is `unpicked`; `test["bar"]` is `nobody` on
  *Nobody else*, else `role` naming the picked label.
- [x] T006 **One step holds it** (`leg_calibrate`, after DRIFT #79's): *each Answer sends its one text ... and each
  Choose picks by label, the served pickedIndex on the wire (keel-web 149; spec 116)* -- every fault
  `{dimension, what, drawn, want}`, recorded and asserted, on the golden and the live walk alike (the page's words
  and the wire are code's on both).

## FR-2 Current solution's two boxes (keel-web 150) -- `49da978`, `70f74a2`, `33e4e9d`

**150 was not merged** into keel-web master (`7a3105f`) when the build ended. Its branch was pushed (`34740c1`, FR-1..FR-3
built, no tasks.md yet), so the ids below are **read from 150's code, not guessed**: the first box is the existing
`textarea.calib__answerbox` with `data-testid="answer-what"`; the second `textarea.calib__howbox`
`data-testid="answer-how"` under `h2.calib__howq` `data-testid="answer-how-q"` (*And how well does that usually go?*,
hint *Where it falls short, in a sentence. Up to 25 words.*); the split and the join are `founderLists.splitAnswer` /
`joinAnswer`. The coordinator should re-check them against 150's tasks.md once it merges.

- [x] T007 **Typed as 150 splits a stored Answer.** `list_answer` detects the second box (`answer-how` drawn) and types
  `split_answer(text)` -- 150's `splitAnswer`: the first box up to and including the first full stop followed by a
  space, the second the rest (left untouched where empty); no such stop, the whole Answer in the first box. Both boxes
  are read back (`seen["boxes"]`), with every hint (`hints`) and the heading (`how_question`). A page before 150 (no
  second box) is typed as before.
- [x] T008 **The one text on the wire.** Around the press `list_answer` keeps the `POST calibration/{vector}/draft`
  (`sent`) and reads its `answer` (`sent_answer`), on every typed list Answer. `answer_boxes_faults` holds it equal to
  `join_answer(*split_answer(text))` (150's `joinAnswer`: the corpus Answer itself, single-spaced) where the two boxes
  were drawn, the one box's text trimmed elsewhere; the boxes to the split; the heading; and the question *How do
  {actor_plural} {job} today?* (`CURRENT_SOLUTION_ASKED`, never the old *How do they deal with it today?*).
- [x] T009 **The screen of record.** `backtest.founder_answer` on `answer-problem.current_solution_satisfaction`
  returns `{what they do (first box), how well it goes (second box), sent as one Answer}` from what the walk typed;
  the corpus text, as before, where the walk drew one box or did not run.

## FR-1's record -- `33e4e9d`

- [x] T010 `founder_answer` on `choose-*` names `picked on screen (by label)`, `drawn at` and `served pickedIndex (the
  wire)` beside the file's `pickedIndex` and item (it said *the served list's item at that index (or its last)*, the
  rule spec 104 retired); `read_back` carries `recall` and `beliefs on screen`.

## FR-3 / FR-4

- [x] FR-3: the pilot screen, the gate, the heard line, the money screener -- untouched.
- [x] T011 FR-4 `tests/test_reworded_founder_screens_116.py` (23): `list_choose` walked in Chromium against a stand-in
  shaped as 149's `ChooseList` (served rows `Nobody else, Their partner, The CFO`, drawn with Nobody else last; the
  PUT carrying the served index) for each of the three picks; the bar's three cases (and the old bars reading no case);
  a page with the old title, Nobody else first, or the drawn position sent is a fault; the faults by name; another
  dimension held to its served index alone; `leg_calibrate`'s wiring; `split_answer` / `join_answer`; `list_answer`
  against 150's two boxes (a two-sentence Answer split, a corpus Answer whole in the first) and against one box; a page
  that drops the second box or asks the old question; the two records.

## Where the spec and the code differ (the code's patterns followed)

- **"The PUT body is today's one text"**: the Answer's Continue sends `POST calibration/{vector}/draft`
  (`{dimension, answer}`, `useRedraftCalibration`), not a PUT; the PUT is Choose's (`PUT calibration/{vector}`). The walk
  asserts each where it is sent.
- **The old *they had to agree last time* / *decided on their own* pins**: the harness pinned neither the old Choose
  title nor the old bar anywhere in code or fixtures (`seen["prompt"]` and `test["bar"]` were recorded, never held), so
  nothing moved; the new pins are new. The strings left in the repo are other things and stay: `brief_facts.py`'s
  *decided on their own* is the brief's Nobody-else fact line (keel-cloud `BriefFacts`), not the Choose bar;
  `quality/scores/*` quote the old bar in cycle 1-3 reads (records, never rewritten); the respondent's *... had to
  agree* answers are the registry's. `buyer_payer_bar` reads the old bars as no case (a test holds it).
- **Faults, not a hard stop per screen**: as 114's `pilot_pick_faults`, each miss is a fault and one step asserts them
  all, so the bundle shows every miss of the stage at once.

## What the spec did not foresee

1. **150 not merged at the build's end** (above): the ids are 150's branch code's; if its tasks.md names others, only
   `ANSWER_HOW_TESTID` / `ANSWER_HOW_Q_TESTID` (and `ANSWER_WHAT_TESTID`, unused: the walk reads the first box by
   `.calib__answerbox`, which 150 kept) move.
2. **No corpus Answer for Current solution has a full stop.** Every entry's Answer (golden 01-07, back-test 08-35) is
   the phrase and the rung labels joined by *;* (`vs.answer_text`), so on every walk today the first box takes the
   whole Answer and the second stays empty -- the two-sentence path runs on the stand-in only. 150's spec already says
   the corpus's rung-list Answer for this dimension is a revision the founder decides; the walk needs no change when
   it moves.
3. **Shot before typing**: the `answer-*` screenshot (and `READ_JS`'s record) is taken as the screen opens, before
   either box is typed, as on every Answer screen; the boxes' words reach the record through `founder_answer` (T009),
   not the shot.
4. **The acceptance walk** (a back-test on the local stack) is the coordinator's: it shows the two writes, the served
   index and the bar's case in the bundle. Not run here.
