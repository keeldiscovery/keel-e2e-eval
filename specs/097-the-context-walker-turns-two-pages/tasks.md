# Tasks 097 -- The harness's context walker turns two pages: the four fields, then the recall window's own page

Branch `097-the-context-walker-turns-two-pages` (worktree `wt/keel-e2e-eval-097`, its own `make venv`), off master
`1fdad29` (099's docs). Built by Claude on 2026-10-30. Read only: keel-web at `1d83a28` (141 merged: `ContextStep.tsx`,
`routes/founder/corridor/ContextRoute.tsx`, `translate.ts`, `recallWindow.ts`), keel-cloud-docs at `f4ca175f`. **No
stack, no browser beyond the unit tests' local Chromium, no model, no paid call.** Nothing merged into master; the
branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `763f1cf` | FR-1 / FR-2: `Corridor.context` turns the page, `context_confirmed` reads the saved window on 2 of 2; the leg holds the window page |
| `cb02a52` | FR-3: `context-window` a founder screen of record (the back-test's answers, the readers' screen kinds) |
| `31905ba` | tests: `tests/test_context_two_pages_097.py` (33) |
| the docs commit | this file and `AGENTS.md`'s spec-097 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| master `1fdad29`, keel-web `1d83a28` (099's count) | 4,294 | 0 | 56 |
| **branch at `31905ba` (the last code; the docs commit adds none), the same keel-web** | **4,327** | **0** | **56** |

+33 passed: `tests/test_context_two_pages_097.py`'s 33. None removed, none re-pinned: no unit test walked the context
form's window (master's pins read the tracker, `_save_context` and `context_reopened`'s occasion line, all kept).

## The checklist

- [x] T001 **The selectors** (FR-1, `harness/vectors_screens.py`): `CONTEXT_SCREENS` (`fields`, `window`),
  `CONTEXT_CONTINUE_TESTID` (`context-continue`), `CONTEXT_WINDOW_PAGE` (`[data-testid=context-window-page]`),
  `CONTEXT_WINDOW_PATH` (`/define/context/window`), `RECALL_UNIT_CHOOSE` (*Choose*); held to keel-web 141's source and
  `translate.ts` (`CONTINUE_LABEL`, `CONTEXT_SAVE_LABEL`, `RECALL_WINDOW_UNIT_PLACEHOLDER`, `BEFORE_COUNTER`).
- [x] T002 **The walker turns the page** (FR-1, `Corridor.context`): the four fields typed on 1 of 2, `context-filled`
  shot, the states tracker installed, *Continue*, the URL `/define/context/window` and `context-window-page` waited
  for; the back-test camera's `context-window` slug; `_context_window_page` reads 2 of 2 as drawn (counter, screen,
  question, chips and the pressed ones, count, unit, *Back*), picks the chip whose words are the window's
  (`vectors_script.window_words`, keel-web `RECALL_WINDOW_WORDS`) else types the count and chooses the unit, reads the
  controls back, captures the page's text (`context_window`) and the `context-window` screenshot; then `_save_context`
  (2 of 2's *Save and continue*, the only one drawn). `Corridor.window_page` keeps `{drawn, via, words, picked}`. The
  step's name says which path (*Continue, then the recall window on its own page* / *Save on its one screen -- no
  recall window (money alone)*).
- [x] T003 **`window_drawn`** (FR-1): `context-continue` drawn on 1 of 2 (a pre-141 page: `input.cwindow__count` on the
  form, filled there as before). Money alone: no Continue, the form's *Save and continue*, `window_page` None.
- [x] T004 **The states tracker** (FR-1): installed on 1 of 2 so one `form` row spans both screens -- its four boxes
  1 of 2's, its Save 2 of 2's -- and the row gains `fields_screen` / `window_screen` (`data-context-screen`, OR-merged
  over the stay). `context_states_faults` unchanged.
- [x] T005 **The leg holds the window page** (FR-1, `evals/corpus_scenario.py`): `window_page_faults` -- *2 of 2*, the
  root's screen `window`, nothing pre-filled (no chip pressed, the count blank, the unit unpicked), the pick left the
  entry's count and unit; `_hold_the_window_page` asserts it on a strict journey and makes it a finding on a back-test,
  where a gate is served (money alone keeps `_drift_96_guard`).
- [x] T006 **Edit and confirmed** (FR-2, `Corridor.context_confirmed`): after Edit the four boxes and the occasion are
  read on 1 of 2, `edited.screen` (`fields`) and `edited.continue` (*Continue*) recorded, *Continue* pressed, 2 of 2
  waited for (`context-edit-window` shot) and the saved count and unit and `context-save` read there; nothing saved.
  `context_reopened` owes `screen` `fields` and *Continue* where a gate is served.
- [x] T007 **The founder screens of record** (FR-3): `evals/backtest.founder_answer` -- `context` the four fields alone
  where the window had its page (else as before), `context-window` the entry's window and how it was picked;
  `read_back` reads the context's understands for it. `quality/decisions.FOUNDER_SCREENS` gains `context-window`
  (between `context` and `context-card`); `table.fix_location` names it *no model* (the page's own words).
- [x] T008 **Tests** (`tests/test_context_two_pages_097.py`, 33): `Corridor.context` walked in Chromium against a page
  shaped as 141's `ContextStep` (one document, the URL moved by the history API as react-router does, the PUT routed):
  the chip pick (7 nights) and the typed pick (4 weeks), the form row spanning both screens, money alone's one screen,
  a window page on a study with no gate recorded rather than waited out; eight seeded `window_page_faults`;
  `context_confirmed` after Edit; the founder screens; every id, class and word held to keel-web's source (skipped
  before 141).
- [ ] `make eval K=s005`, `K=s015`, `K=s016` on the local stack at keel-web 141 (the spec's acceptance): **not run** --
  this build brings no stack up (the brief's rule); it is the coordinator's step.

## Where the spec and the code differ (the code's patterns followed)

- **"Picks the window as today (a chip where one matches, else count + unit)"**: today's walker never pressed a chip;
  it always typed the count and chose the unit. FR-1's rule is built as written (a chip whose words are the window's,
  else count + unit), so an entry's window that is a preset (7 nights, 7 days, 5 working days, 30 days) is now
  picked by its chip; Countly's 4 weeks is typed; `window_page.via` says which.
- **"Captures the page's text"**: captured under `context_window` (beside the step's `stage_screen`, which stays the
  card's), so the card's text of record does not change.
- **FR-3's readers and rubric**: no prompt in `quality/readers/*.md` and no anchor in `quality/rubric.py` /
  `RUBRIC.md` names the context form's controls -- the founder reader reads screens by slug -- so nothing there moved;
  the new founder screen is the slug `context-window` and its kind in `FOUNDER_SCREENS`. No mark reads the form:
  `MARKS_VERSION`, `INTERVIEWER_MARKS_VERSION` and `RUBRIC_VERSION` stand.
- **FR-3's "gallery"**: `evals/gallery.py` records no founder screen (it exports the briefs, `inputs.json` and the
  respondents' drawn screens); the founder's recorded screens are the back-test bundle's `founder_screens`, which gain
  the window page through the camera's `context-window` slug.
- **A pre-141 page** is still walked (the window on the one form) -- the repo's pattern for a sibling one spec behind
  (`context_occasion` before 117); the leg's window-page hold then names it.

## What the spec did not foresee

- keel-web 141's root keeps `data-context-state=form` on both screens (`data-context-screen` tells them apart), so the
  113 tracker had to be installed before *Continue*: installed on 2 of 2 its form row would read no box and fault.
- Edit's 2 of 2 is drawn from the saved window only because `ContextStep` keeps its mount across the two URLs (one
  route, `define/context/*`); the walk relies on it, and a reload on 2 of 2 with a field blank sends the page to 1 of 2.
- A window page on a study that serves no gate (money alone in the corpus, a gate on the page) cannot be saved; the
  walker records it on `saves` (`status` None) and returns no sentence instead of waiting out the card.
- master moved during the build (`8374e59`, spec 112's spec.md only); the branch was not rebased -- no file overlaps.
