# Tasks: the live journey reads the deck

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**: `027-journey-brief-ship`

`make unit`: **green at every commit on this branch.** Baseline at `736a61e`, before a line was
written: **1,262 passed** (Discovered **D-0**). At the end: **1,283 passed** — twenty-one new tests,
none deleted, and no assertion removed anywhere.

**Tests first, within each phase.** Each phase's own tests are written before the code that turns
them green and land in the same commit (spec 025 D11's rule, kept by spec 026 and kept here). **No
test is deleted**, and no assertion is removed — each one either stands where it stood or stands
somewhere else with the reason above it.

**Nothing below spends a model call.** The only paid thing this branch produces is the command in
*The next live run*, and it is the founder's to type.

## Phase 1 — read before writing anything

- [X] **T001** keel-cloud `canon/designs/brief-page-design.md` (status **APPROVED**) — §3 the deck,
      §4.1 the word budget, §4.3 the rest-of-three limit, §6 the download, §7 what leaves the
      overview.
- [X] **T002** keel-web `specs/027-brief-ship/spec.md` and its `tasks.md` **Discovered** — FR-001…
      FR-032, FR-013/FR-014 struck, SC-003/SC-006/SC-008/SC-009, and D-01…D-23.
- [X] **T003** keel-web's **own markup at master `7e5a2a8`** — `OverviewRoute.tsx`,
      `PrintRoute.tsx`, `components/brief/ShipFigure.tsx`, `components/brief/StagePanel.tsx`,
      `components/brief/lines.ts`, `lib/translate.ts`, `styles/app.css`. The markup is what a page
      object reads, and reading only the prose is how a referee writes an assertion against a screen
      that does not exist (spec 026 D-3, and the lesson that produced this branch).
- [X] **T004** keel-web `specs/028-phone-shell/` and `specs/029-phone-pages/` — merged locally, not
      deployed. What they keep (the deck) and what they add (a bottom tab bar on phones).
- [X] **T005** this repository's own blast radius: `harness/browser.py` (`Overview`, `PrintPage`),
      `harness/rubric.py` (every `captured_text` key it reads), `evals/policy.py` (`RETIRED_STRINGS`,
      the stage-name enum exemption), `evals/test_s001_smoke.py`, `evals/corpus_scenario.py`,
      `evals/test_s005_countly.py`, `evals/test_s007_mulchrun.py`, `evals/test_s002_agent_optional.py`,
      `evals/test_s003_every_door.py`, `evals/tools/curated_proof_run.py`,
      `tests/test_page_object_calls_exist.py`, `tests/test_journey_coverage.py`.
- [X] **T006** the red run: matrix run **36870786241**, staging keel-cloud **782a01a**, keel-web
      master **7e5a2a8**, project at revision 34, failing at §1.7 on
      `wait_for_selector(".ocards, .guided-step")`.

## Phase 2 — the page objects read the deck and the brief (FR-001 … FR-013, FR-026 … FR-028)

- [X] **T010** `tests/test_journey_brief_ship_markup.py` (new, 21 cases): keel-web's own markup for
      the deck and the five-page sheet, condensed to the nodes the page objects read, driven through
      `Overview` and `PrintPage` in a real Chromium. Includes **the red run reproduced** (T011) and
      the two scope traps (T012).
- [X] **T011** the red run's own assertion, offline: `wait_for_selector(".ocards, .guided-step")`
      raises on the deck, and `Overview.DECK` matches it. `.ocards` is still a live keel-web class on
      `StageRoute`'s opened card (keel-web D-10) — **D-1**.
- [X] **T012** the two scope traps as their own cases: the paragraph reader on a sheet whose page 1
      has no paragraph and whose stage pages have three `p.pclaim` (**D-2**), and the stage-table
      reader on a sheet with four `table.ptab` (**D-3**).
- [X] **T013** `harness/browser.py::Overview` — `DECK`, `AFFORDANCE`, `PANEL_HELD`,
      `PANEL_DID_NOT_HOLD`, `is_deck`, `ship_label`, `ship_caption`, `ship_counts`, `bands`,
      `panels`, `panel`, `part_of`, `lines_of`, `tail_of`, `worst_panel`, `open_every_tail`,
      `foot_line`, `five_words`, `people_line`, `deck_text`, `download_state`, `open_panel`, and
      `download` returning the page the sheet landed on.
- [X] **T014** the retired readers kept and documented: `evidence_line`, `percent_line`,
      `lines_with_answers`, `legend`, `stage_cards`, `what_this_says`, `what_this_says_paragraph`,
      plus `legend_present` and `carries_what_this_says` beside the two whose empty answer is
      ambiguous.
- [X] **T015** `Overview._capture` — the deck's own three keys (`ship_caption`, `ship_label`,
      `panels`), the download's state, and `affordance` off `Overview.AFFORDANCE`. The
      `what_this_says` key **leaves** this capture and reappears under the same name in
      `PrintPage._capture` (**D-4**).
- [X] **T016** `harness/browser.py::PrintPage` — `PAGE`, `EVIDENCE_COLUMNS`,
      `WHAT_THIS_SAYS_HEADING`, `page_count`, `page_one`, `title_page` re-pointed, `handoff_line`,
      `what_this_says_heading`, `what_this_says_paragraph`, `what_this_says`, `block_169`, `parts`,
      `table_columns` re-scoped, `evidence_page`, `participant_names`, `print_was_called`, and
      `stub_print` on the context.

## Phase 3 — §1.7 of the live journey (FR-014 … FR-020)

- [X] **T020** `evals/test_s012_journey_through_a_host.py`: the pre-invite step — every stage
      approved, nobody asked, the deck standing and the download the disabled *Nothing to hand over
      yet* control with its why. The only moment that state can be read, and the place the retired
      *What this says* "not yet" assertion now stands (**D-5**).
- [X] **T021** `_WASH_OF_VERDICT`, `_WORST_FIRST`, `_band_wash`, `_stage_lines`, `_worst_stage` —
      keel-web's own four helpers restated in Python beside a comment saying where they were read
      from, so the deck can be compared against the wire without anything being recomputed
      (plan Decision 4).
- [X] **T022** §1.7's own six steps: the paragraph's wire half (poll kept verbatim); the deck's three
      bands and three panels; each panel's count line against the wire; the worst panel open at rest;
      the download live; and the brief — five pages, page 1's paragraph and 16:9 block, page 5's
      counts and no names.
- [X] **T023** the three retired assertions, moved with the reason above each: the paragraph's screen
      half to page 1 of the sheet, the three stage cards to the three panels, and the four-count
      legend to `GET /standing`'s own four lists (**D-6**).

## Phase 4 — the sweep (FR-021 … FR-025)

- [X] **T030** `evals/test_s001_smoke.py`: the pre-reading step inverted, the bar and legend steps
      become the deck's, the paragraph step moves to §1.10, the stage-cards step becomes the panels'.
- [X] **T031** `evals/corpus_scenario.py`: `_assert_overview` reads the deck;
      `_assert_no_paragraph_yet` inverted; `_assert_what_this_says` takes the `PrintPage` and is
      called after the sheet is open; `_assert_download` gains page 1 and page 5; `expected_legend`
      kept and compared against the panels' rows.
- [X] **T032** `evals/test_s005_countly.py`: every one of the mockup's five numbers kept, read off
      the deck — except *not asked yet*, which the deck draws nowhere and which is asserted against
      the wire with the reason above it (**D-6**). A second step ties the mockup's four counts to the
      deck's three rows, so neither human statement can be edited alone.
- [X] **T033** `evals/test_s007_mulchrun.py`: the metric-leak sweep reads the deck's own text and the
      printed paragraph.
- [X] **T034** `evals/tools/curated_proof_run.py`: the overview and download blocks read the new
      readers.
- [X] **T035** `harness/rubric.py` and `evals/policy.py` read for anything whose *meaning* moved.
      **Nothing did**, and the reasons are **D-4**, **D-7** and **D-8**.

## Phase 5 — the ledger and the governing documents

- [X] **T040** this `tasks.md`'s `## Discovered`, written as the work found things and not after.
- [X] **T041** `AGENTS.md` and `README.md` — one paragraph each, beside the paragraph spec 026 put
      there, naming the deck, the red run and that nothing was dropped. **D-10.**
- [X] **T042** the whole repository grepped for the retired selectors, not only the page object the
      red run named: `ReviewCard.continue_onward`'s own wait had `.ocards` in it too (**D-12**).

## Phase 6 — the command

- [X] **T050** *The next live run* below: the dispatch inputs, written down and not typed.

## Discovered

A ledger of what the work found that the documents did not say, in the order it was found. Each
entry names where it was found and what was done about it.

- **D-0 — the baseline.** `make unit` at `736a61e`, before a line was written: **1,262 passed in
  153.94s**. Recorded so every later number on this branch has something to be compared with.

- **D-1 — the selector that cost run 36870786241 was not stale, it was *live on another screen*.**
  The obvious reading of the red run is *keel-web deleted `.ocards`, so change the selector*. keel-web
  spec 027's own Discovered **D-10** says the opposite in as many words: `.ocards` and `.minibar`
  "keep a caller, so they were not deleted" — `StageRoute`'s own opened card draws
  `<div className="ocards">`, and deleting either would have taken the stage page's rail with it.
  What *was* deleted is `.evidence`, `.evidence__head`, `.evidence__title`, `.evidence__pct`,
  `.evidence__people`, `.evidence__actions` and `.handoff`. So the wait was for a real class on a
  different screen, which is the one shape of selector bug that a grep for the class name finds
  nothing wrong with. **The markup test therefore asserts the timeout rather than the absence**
  (`test_the_old_wait_really_would_have_timed_out_on_the_deck`): absence is not what went wrong.

- **D-2 — page 1's paragraph and a stage page's claim are both `p.pclaim`, and a sheet-wide read
  would have compared the wrong two things.** `PrintRoute` renders `<p className="pclaim">
  {whatThisSays}</p>` on page 1 and `<p className="pclaim">{summary.claim}</p>` on each of pages
  2–4 — two different wire fields with two different authors, under one class. A reader scoped to
  the sheet would have compared `StageSummary.claim` for the problem stage against
  `Overview.whatThisSays` and failed on a correct product; worse, on a project where the model's
  paragraph happened to open with the problem's claim it would have *passed on the wrong sentence*.
  `PrintPage.what_this_says_paragraph()` is scoped to `.pages > .page` nth(0), and
  `test_the_paragraph_reader_is_scoped_to_page_one_and_never_reads_a_stages_claim` draws a sheet with
  no paragraph and three claims to prove it.

- **D-3 — page 5 is a `table.ptab` too, so `table_columns()` broke on a sheet nobody had changed
  yet.** `PrintPage.table_columns()` read every `table.ptab` on the sheet and its two callers
  (`evals/test_s001_smoke.py` §1.10 and `corpus_scenario._assert_download`) assert
  `[list(COLUMNS)] * 3` and then loop over every row asserting the three named stage columns.
  keel-web FR-029's evidence table carries *Line · The question asked · Where they landed · Counted*,
  so the read answers four rows now and the fourth fails the loop. **Found by reading `PrintRoute`,
  not by a run** — neither S-001 nor the corpus scenarios are in `make unit`, so this would have
  been the next red stack run after the one the branch was opened for. Re-scoped to the stage pages;
  `evidence_page()` reads the new one; `table_rows(index)` deliberately stays indexed over the
  sheet's own tables so `3` is the evidence table.

- **D-4 — the `what_this_says` capture key had to move, and moving it is what keeps CLA-U1/CLA-U2/
  CLA-U4 reading the paragraph at all.** `harness/rubric.py` sweeps every `captured_text` value
  except `NOT_RENDERED_TEXT` for raw enums (CLA-U1), structural leaks (CLA-U2) and retired strings
  (CLA-U4). The paragraph reached that sweep because `Overview._capture` captured it. Left alone,
  the key would simply have stopped being written and the three checks would have gone on passing
  over a screen that no longer carries the sentence — a silent loss of coverage, which is exactly
  what this repository's own policy history calls the worst shape a green run can have. So the key
  **leaves `Overview._capture` and reappears, under the same name, in `PrintPage._capture`**. No
  check changed; the screen the key is captured on did.

- **D-5 — the "not yet" note is now rendered nowhere, so its assertion had to be inverted rather
  than moved.** `evals/test_s001_smoke.py` and `corpus_scenario._assert_no_paragraph_yet` both
  assert that before the first reading the overview shows keel-cloud's own `whatThisSaysNote`
  (`shown == note`). The paragraph moved to page 1 of the sheet — and `PrintRoute` prints **no
  note**: keel-web's own comment is that "a sheet does not explain to itself why a block it left
  out is missing". So there is no screen left that draws the note, and the assertion cannot move.
  **It is inverted instead**, in three parts, with the reason above it: the wire still carries no
  paragraph and still composes a note (both still asserted, on the wire); the overview carries no
  *What this says* block at all (`carries_what_this_says()` False); and the founder-facing sentence
  for *there is nothing yet* is the download's own disabled state — *Nothing to hand over yet*, with
  *The brief fills as your AI reads answers.* beside it (keel-web FR-025 state 3). Which is a better
  reading of the same moment than the one it replaces: the note was a sentence about a paragraph the
  founder had not asked for, and the disabled control is a sentence about the thing they came to do.

- **D-6 — the four-count legend has no successor on any screen, so one of the four counts is
  asserted against the wire and said so.** keel-web FR-020 took the four-word legend off the
  overview with the bar. The deck shows each stage's `holdingUp` as its HELD rows and its
  `notHoldingUp` + `peopleDisagree` as its DID NOT HOLD rows — so three of the four counts are still
  readable off the screen, summed over the three panels (with every tail opened, `open_every_tail()`).
  **`untested` is drawn nowhere on the deck**: a line nobody could answer appears in no part, and
  `panel__count`'s *N of M lines holding* carries it only inside its denominator. So S-005's
  mockup-of-record step keeps all five of its numbers — 9 holding up, 3 not holding up, 6 people
  disagree, 0 not asked yet, 18 lines — and reads the first three plus the fifth off the deck and the
  fourth off `GET /standing`'s own `untested` list, with that sentence written above it. No number
  was dropped; one of them changed which party is asked for it.

- **D-7 — the BRIEF paragraph's own four marks are not a scenario's to apply, and were not wired
  in.** The brief for this spec asked that "every existing paragraph assertion (register, no stage
  labels, the deciding number)" be kept on the printed paragraph. Those three are
  `instructions/brief.py`'s marks — `register` (second person and the market's own currency),
  `shape` (which checks the paragraph names no raw `PROBLEM`/`SOLUTION`/`COMMERCIAL`) and `coverage`
  (the deciding line's number quoted exactly beside the founder's own phrase) — and they are applied
  by the **instruction eval**, to a model's answer, under `instructions/marks.py`'s `MARKS_VERSION`.
  The `Makefile`'s own words for that subsystem are that it "never reads or writes evals/policy.py —
  its own rubric is versioned separately", and the reverse holds. Wiring them into a scenario would
  have made a rubric change out of a selector fix and would have put a paragraph's *quality* on a
  journey whose subject is whether the journey works. **So what moved to the sheet is what the
  journey actually asserted**: the paragraph is non-empty on the wire, and page 1 renders it byte for
  byte. `no stage labels` is additionally **not** something CLA-U1 could have carried either —
  `evals/policy.py`'s judgement call 1 exempts the three stage names from the enum sweep by name,
  because `STAGE_LABEL`'s own copy renders *THE PROBLEM* on half the product's screens.

- **D-8 — `RETIRED_STRINGS` was deliberately not extended, and the reason is a live caller.** CLA-U4
  fails a bundle where a retired string survives into rendered founder-facing text, and spec 027
  retired a lot of copy from the overview: *18 of 18 lines have answers*, *all tested*, the four
  legend words, *Open · N lines ›*, `dealBreakersHoldingTail`'s own row. Adding any of them would
  have gone red on a correct product: keel-web FR-020's own closing sentence is **"None of those
  words is deleted from `translate.ts`"**, and several still render — `openLinesLabel` and the
  deal-breaker row on `StageRoute`'s opened card, the legend words as the four status words
  everywhere. A retired *string* and a retired *screen* are different things, and `RETIRED_STRINGS`
  is about the first. Left unchanged, and `evals/policy.py` is byte-identical on this branch.

- **D-9 — keel-web FR-016 says the worst panel's band is lit at rest, and the built deck lights no
  band at rest.** The spec's own wording is that on the desktop deck the worst panel "is expanded
  (tails opened) and its band is lit". `OverviewRoute.tsx`'s `Deck` initialises its emphasis state as
  `useState<StageType | null>(null)`, and `lit` is set only by `onMouseEnter`/`onFocus` on a band or
  a panel — so at rest no band carries `.lit`, which is also what FR-006's *emphasis, never
  disclosure* asks for. `Overview.bands()` reads `lit` and the journey **records it without asserting
  it**; what is asserted is the `panel--worst` marker and the absence of a tail, which are the two
  things the DOM actually carries (plan Decision 5). Worth one look from the founder beside keel-web's
  own open questions, and not a failure.

- **D-10 — `AGENTS.md` and `README.md` each needed one paragraph, in the place spec 026 put
  its own.** Both describe S-012 by what it asserts, and both carry a *"and what it asserts about
  the cards moved when keel-cloud 048 moved it"* paragraph from the branch before this one. A
  paragraph each is added beside it, naming the deck, naming the red run, and naming that no
  assertion was dropped — which is the sentence a reader of a green bundle needs in order to tell a
  run taken under this spec from one taken before it. `README.md`'s historical run notes are left
  exactly as they were: *"`whatThisSays` was still not observed rendered on a live overview"* is a
  true record of what run 36563095946 found, and rewriting a run's own findings is not this
  repository's practice.

- **D-11 — `tests/test_page_object_calls_exist.py` is why the retired readers are kept, and it says
  so by passing.** The static check walks each scenario's AST and asserts every attribute reached
  through a page-object local exists on the class. `evals/test_s005_countly.py`,
  `evals/test_s007_mulchrun.py`, `evals/test_s001_smoke.py`, `evals/corpus_scenario.py` and
  `evals/tools/curated_proof_run.py` between them name `evidence_line`, `percent_line`,
  `lines_with_answers`, `legend`, `stage_cards`, `what_this_says`, `what_this_says_paragraph`,
  `download_link_text`, `download`, `title_page` and `table_columns`. Deleting any one of them would
  have turned a scoped change into a repository-wide one in the same commit — and would have done it
  *in `make unit`*, which is the one place this repository finds that class of mistake cheaply
  (`runs/DRIFT.md` #33). Every one is kept, every one answers empty or is re-pointed, and the check
  passes untouched.

- **D-12 — `ReviewCard.continue_onward` waited for `.ocards` too, and on the last stage it
  would have cost twenty seconds on every run.** Found by grepping the whole repository for the
  retired selectors rather than only the page object the red run named. The approved card's onward
  door is *Continue to step N* or, on the last stage, *Go to People*; the wait after it was
  `".chat, .ppl, .role, .ocards"`, and that fourth alternative was the overview — which is the deck
  now. It is not the fault that killed run 36870786241 (the method's URL fallback and the People
  page's own classes carry the common cases), but it is the same fault one axis over, and it would
  have been silent: a twenty-second wait that ends in a timeout `wait_for_selector` raises on, in a
  method no scenario asserts the duration of. Widened to the deck's three classes plus
  `.guided-step`, with `.ocards` kept at the end for a deploy that predates the deck.

- **D-13 — the download opens a second tab, so S-001's own `overview.download()` had to learn to
  answer which page it landed on.** keel-web FR-025 gives the ready control `target="_blank"` and
  `rel="noopener"`, so the founder's click leaves the overview standing behind the sheet — which is
  the design's point (§6.1 decision 4) and which `_wait_for_url_change` on the original page can
  never see. Two consequences, both handled rather than worked around. `Overview.download()` opens
  the popup through `context.expect_page()` and **returns the `Page`**, falling back to the
  in-place navigation so it still works against a deploy that has not shipped the attribute; and
  `PrintPage.stub_print()` installs its `window.print` no-op on the **context**, because a
  page-scoped `add_init_script` is not inherited by a tab the click opens and an unstubbed
  `PrintRoute` raises a native dialog no locator can dismiss. S-012 does not take the click at all
  (plan Decision 6): it asserts the link — label, enabled state, `href` — and then reaches the
  sheet by URL in the one page it already has.

- **D-14 — the sheet was five pages before this and is five pages after it, which is why nobody
  noticed it had been rewritten.** `evals/test_s001_smoke.py` and `corpus_scenario._assert_download`
  both assert `len(sheets) == 5`. Until keel-web 027 that was a title page, an overview page and
  three stages; now it is page 1, three stages and the evidence page (keel-web FR-029/FR-030,
  SC-008). The count assertion is correct in both worlds and proves nothing about either, so both
  steps gained the composition beside it — page 1's name and hand-off line, the 16:9 block's
  presence, and page 5's four columns and no names. A count that cannot fail is not a check, and
  this one had been passing over a rewrite.

## The next live run

Nothing on this branch spends anything. These are the inputs for the founder's next live S-012 run,
against a staging twin carrying **keel-cloud 782a01a or later** and **keel-web master 7e5a2a8 or
later** (the build this branch was written against; keel-web 028/029 are merged locally and not
deployed, and nothing below assumes them).

**By hand, from this checkout:**

```
make eval-live K=s012 HOST=claude LEGS=full ENTRY=03-lullaby PEOPLE=5 PROFILE=remote
```

**As a matrix dispatch** (`.github/workflows/matrix.yml`, the same shape run 36870786241 used):

| input | value |
|---|---|
| `set` | `nightly` |
| `cells` | `macos-15-claude-py3.13` |
| `legs` | `full` |
| `entry` | `03-lullaby` |
| `people` | `5` |
| staging | keel-cloud **782a01a**, keel-web master **7e5a2a8** |

**What to read in the bundle, in this order**, because these are the steps this branch wrote:

1. *§1.7: with every stage approved and nobody asked, the deck stands and there is nothing to hand
   over yet* — the one moment the disabled download exists.
2. *§1.7: the deck — one band per stage, coloured by the verdict the wire sent, and one panel per
   band saying it in words*.
3. *§1.7: each panel's count line is the wire's own three numbers, and each one carries at least one
   line that held or did not* — its `per stage` block is the whole comparison, screen against wire.
4. *§1.7: the worst stage's panel is the one open at rest*.
5. *§1.7: now a reading exists, Download the brief is live*.
6. *§1.7: the brief is five pages, and page 1 carries the paragraph under its own heading and the
   16:9 block*.
7. *§1.7: the evidence page counts every line and names nobody*.

**What a failure in each one means, so the founder need not guess:** 1 and 5 are the download's two
states and a failure in either is keel-web's; 2 is a band coloured for a verdict `GET /overview` did
not send; 3 is a count line and the wire disagreeing, and its `faults` list names the stage and both
numbers; 4 is keel-web marking the wrong panel worst or closing the right one; 6 is the paragraph not
printing verbatim, or the sheet not being five pages; 7 is a participant's name on the page that gets
forwarded, which is principle P8 and the one failure here that is not cosmetic.
