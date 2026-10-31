# Tasks 114 -- The lock walk picks Yes or No on the pilot screen, and reads the window card once

Branch `114-the-lock-walk-picks-the-pilot` (worktree `wt/keel-e2e-eval-114`, its own `make venv`), off master `c58f519`
(106's docs; 4,582 / 0 / 56). Built by Claude on 2026-10-31. Read only: keel-web master -- `23c7596` (146) when the
build started, **`d6dc5a9` (147 merged) by the time it ended** -- `src/components/corridor/BeforeStep.tsx`,
`src/lib/translate.ts`, `src/lib/founderLists.ts` (`commitmentStep`), `src/lib/contextReach.ts`, 146's and 147's
tasks.md; keel-cloud-docs master `e68c0de4` (the corpus and back-test entries). **No stack, no model, no walk, no paid
call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `5486588` | FR-1 / FR-2: the pilot pick in the walk and the leg; the window-line rule (147 off, as master stood then) |
| `028acd8` | FR-3: `tests/test_lock_walk_pilot_114.py` (31) |
| `8b8b49b` | FR-2: keel-web 147 merged meanwhile -- the rule turned on, the tests moved with it |
| the docs commit | this file and `AGENTS.md`'s spec-114 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `c58f519` as 106's tasks.md records it (keel-cloud-docs `1acc3791`, keel-web `23c7596`) | 4,582 | 0 | 0 | 56 |
| **branch at `8b8b49b`, keel-cloud-docs `e68c0de4`, keel-web `d6dc5a9`** | **4,604** | **6** | **5** | **54** |

+31 tests, all this spec's (4,582 + 56 + 31 = 4,669 = 4,604 + 6 + 5 + 54). **None of the 11 is this spec's**: each
fails or errors the same way on `origin/master` (`c58f519`) against the same siblings, which I ran on those three files
in a scratch worktree that I then removed: 6 failed, 5 errors. They all come from **keel-cloud-docs spec 174** (FR-2
`fdd8d3e7`, *Purchase friction ... I can't tell*): the registry now gives `commercial.purchase_friction` the one escape
`cant_tell`, while the corpus and back-test entries still say `cant_recall`, so `instructions.corpus` refuses
`05-paidly`, `10-palus`, `17-expanse`, `21-codyco` (*the registry's one escape is 'cant_tell' (spec 042 ...)*):

- `tests/test_corpus_r11_shape.py::test_the_corpus_reads_the_same_through_the_exported_registry`
- `tests/test_lock_frontier_110.py`: `test_a_record_written_after_170_keeps_every_rule`,
  `test_a_record_before_170_is_skipped_by_name`, `test_the_three_entries_cost_items_are_170s_lines` (×3)
- `tests/test_instruction_spoken.py`: five errors at setup (`test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart`,
  `test_the_record_follows_registry_revision_13s_five_changes`, `test_the_ability_four_are_the_registrys_own_words`,
  `test_a_known_item_no_longer_found_is_still_a_fault_were_one_named`, `test_a_selection_of_entries_marks_those_alone`)

I left them alone (the corpus is keel-cloud-docs', and its builder was still at work). The two skips fewer (56 -> 54)
come from the same moves in the siblings. I did not check them one by one.

## The checklist

- [x] T001 **FR-1 the walk reads the pilot screen as it opens** (`harness/vectors_screens.py`,
  `Corridor._pilot_opened`). The spec gave `~:1984-2045`; the ready step is `word_pilot_and_lock` (now `:2100`ff).
  The walk reads the `pilot-pick` radiogroup (role, label), the quoted step
  (`pilot-first-step`, *Your first step: {step}*; with `step=True` it waits up to 10 s, because the page draws the step
  once the COMMERCIAL calibration read lands), each card (`testid`, `role`, words, `aria-checked`), `before-continue`'s
  words and `disabled`, and how many text boxes and checkboxes the card holds. The `ready-pilot` shot is taken after
  that read and before the pick, so the screen stays a founder screen of record as it opened. The new constants are
  `PILOT_PICK_TESTID`, `PILOT_CARDS`, `PILOT_FIRST_STEP`, `BEFORE_CONTINUE_TESTID`, `WORD_PATH`, `PILOT_SETTLE_MS`,
  `pilot_continue(yes)` and `pilot_testid(yes)`.
- [x] T002 **FR-1 the pick** (`Corridor._pilot_pick`). It taps *Yes, ask them* or *No pilot* and waits for that card's
  `aria-checked="true"`. It keeps every `PUT /v2/projects/{id}/word` the pick sent: *No* waits for the PUT's answer,
  and *Yes* gets `PILOT_SETTLE_MS` (1.5 s) in which a write it should not send would show up. It reads the screen again,
  waits for Continue to come alive and presses it with its label (*Continue · Yes* / *Continue · No*), then waits for
  who asks. The plain-*Continue* press (`_button(self.page, BEFORE_CONTINUE)`) is gone. `word_pilot_and_lock` gains
  `pilot_yes` and `step`, and `ready["pilot"]` holds `{group, step_line, step, opened, textboxes, checkboxes, picked,
  after, pressed, writes}`.
- [x] T003 **FR-1 which pick** (`harness/vectors_script.founder_pilot`). The answer is Yes on every entry. I searched
  every golden and back-test YAML in keel-cloud-docs, and none records a founder who opts out. The people with
  `pilot_opt_in` expect the line at the end (spec 067 FR-6). An entry object with `founder_pilot = False` would pick
  *No*, so the No branch is wired and tested, but no walk takes it today.
- [x] T004 **FR-1 the hold** (`evals/corpus_scenario.py`: `commitment_step`, `stored_first_step`, `pilot_pick_faults`,
  `_hold_the_pilot_pick`, called from `leg_lock` on every scope except PROBLEM). `commitment_step` mirrors keel-web 146's
  `commitmentStep`: `commercial.commitment`'s `answer.list.items[pickedIndex ?? 0].label`, trimmed, or None where the
  step is left out or unsaved. `stored_first_step` reads it from `GET calibration/COMMERCIAL` only where the money is in
  scope, and SOLUTION makes no read, as on the page. `pilot_pick_faults` checks each of the following and names one
  fault per miss:
  - the open state: two radio cards with 146's words, neither checked; Continue reads *Continue* and is disabled;
    no text box and no checkbox;
  - the quoted step: equal to the stored step where one is stored, absent where none is;
  - after the pick: the picked card is checked alone, and Continue is live and named;
  - the label pressed;
  - **the PUT on No only**: exactly one, `pilotEnabled: false`, answered 2xx. On *Yes* nothing is written, because a
    new project's stored opt-in is already true.

  The step asserts, strict or not: the screen is the page's code, not a model's words.
- [x] T005 **FR-1 the screen of record** (`evals/backtest.founder_answer`). `ready-pilot` now answers
  `{"pilot": {"step", "picked"}, "pressed": "Continue · Yes"}`, read from `j.changed["pilot"]` (which the leg writes),
  instead of `"Continue"`. `persona-who-answers` keeps *Continue*. The readers render it as before ("What was typed or
  picked here").
- [x] T006 **FR-2 the window line** (`evals/corpus_scenario.py`: `WEB_147_BUILT`, `web_147_built`, `window_line_owed`,
  `window_line_faults`; `harness/vectors_script.read_back_says_window`, which mirrors 147's `readBackSaysWindow` regex
  byte for byte). **keel-web 147 was not on master when the build started (`23c7596`). It merged during the build
  (`d6dc5a9`), so FR-2 is built for 147 on master.** On a windowed card no *Counting the last ...* line is owed where the
  served sentence ends *We'll ask about the last ...*, which is every fresh project since keel-cloud 168. The line is
  owed, with the founder's window words, on an old sentence. `KEEL_WEB_147=0` turns the old pin (the line on every
  windowed card) back on for one run against a build before 147. `leg_context`'s pin
  (`assert vs.window_words(founder.window) in window_line`) now goes through `window_line_faults`, and its record owes
  the window words only where the line is owed.
- [x] T007 **FR-2, the pins the spec named.** Line numbers had moved, and one pin was not what the spec took it for:
  - `evals/corpus_scenario.py ~:677` (103 tasks.md's `:679`) is `needs_input_answer`'s *Counting the last {window}.*.
    That is **the founder's own answer** to a context `NEEDS_INPUT`, text typed to Keel, not the card's muted line, so it
    is untouched. The card's pin was in `leg_context` (`:413` before this change), and that pin moved (T006).
  - `tests/test_drifts_95_97_closed.py ~:134` is the money-alone family (`:150`, the card's *Counting the last 7
    nights.* fails DRIFT #96's guard). It **stands either way**: money alone serves no window, so the line never
    appears, before 147 or after. A new test confirms this under both flag values. Only that file's `leg_lock` stub
    changed, to take the new keyword arguments (`**_`).
- [x] T008 **FR-3 tests** (`tests/test_lock_walk_pilot_114.py`, 31). The walk runs in Chromium against a page shaped like
  146's step 5 (the word's address redirecting, the pilot screen, who asks, the lock, *Sent*), covering:
  - **the pilot screen walked:** the cards on open, Continue disabled, the pick and the label, the PUT on No and none
    on Yes, the quoted step, shots taken before the pick; no step where none is stored; a quoted step where none is
    owed; plain Continue going nowhere; a pre-ticked card, a live Continue or an offer box each a fault; Yes on a
    stored opt-out writes and is named;
  - **the faults one at a time:** eleven, each named;
  - **the leg and the records:** `commitment_step` and `stored_first_step` per scope (SOLUTION makes no read);
    `founder_pilot`, with the corpus searched for a founder opt-out; `leg_lock` asking for the pick, holding it,
    stopping on a plain Continue, and recording the `ready-pilot` answer; the problem study with no pick;
  - **the source checks:** the walker no longer presses plain Continue; 146's words held to keel-web master's
    `translate.ts` and `BeforeStep.tsx`;
  - **the window line both ways:** 147 on (the default now) and off (`KEEL_WEB_147=0`); the regex mirror held to
    keel-web master's `contextReach.ts`; `leg_context` through the rule; money alone failing on a drawn line under
    either flag value.

## Judgement calls

- J-1 **The Yes write is held to "none".** The spec says the PUT is asserted on No only. The walk's projects are new
  (stored `pilotEnabled: true`), so a Yes that writes means a page that ignores the stored opt-in. That is a fault the
  leg names, not something passed over.
- J-2 **The step is compared with the stored step, not the file's.** The page quotes what the COMMERCIAL calibration
  stores, which is the founder's saved list (on a back-test that can be Keel's draft as picked), so the leg reads the
  wire as the page does. Where the money is in scope but no step is stored, no line is owed.
- J-3 **The flag follows 131's pattern** (`interview_charge.WEB_131_BUILT`, with an environment override), not a run-time
  read of the sibling checkout. Remote walks build no web from `../keel-web`, so its source is not the page they read.

## What the spec did not foresee

- keel-web 147 merged while 114 was being built, so FR-2 is built for the merged case (T006). The pre-147 pin stays
  reachable with `KEEL_WEB_147=0`.
- The `~:677` pin is the founder's NEEDS_INPUT answer, not the card's line, and 103 tasks.md (T011) misread it too
  (T007).
- No corpus entry records a founder who opts out of the pilot, so no walk walks *No* (T003).
- keel-cloud-docs 174 left master red here: 6 failed and 5 errors, from the Purchase friction escape `cant_tell` against
  the corpus's `cant_recall` (Unit, above). That is not this spec's to fix.
