# Feature Specification: the live journey reads the deck — the overview's bar, legend and cards become the ship and three panels, and *What this says* is asserted on the brief it now prints on

**Feature Branch**: `027-journey-brief-ship`

**Created**: 2026-10-01

**Status**: **Draft for implementation.** Nothing here spends anything. The one paid thing this
spec produces is a *command* — the founder's next live S-012 run — and it is written down in
*The next live run* below rather than typed by this pass.

**Input**: the designs, specs and markup of record, read in full —

- keel-cloud [`canon/designs/brief-page-design.md`](../../../keel-cloud-docs/canon/designs/brief-page-design.md)
  — **status APPROVED**. §3 (the deck: the ship as mark 1a sliced into three, position means stage
  and colour means verdict, the panels, **HELD and DID NOT HOLD and no third part**), §4.1 (the word
  budget), §4.3 (the rest-of-three limit, set by the slide test), §6 (the download: five pages, what
  page 1 carries, what page 5 carries, and the P8 no-names rule), §7 (what leaves the overview).
- keel-web [`specs/027-brief-ship/spec.md`](../../../keel-web/specs/027-brief-ship/spec.md) and its
  `tasks.md` **Discovered** — FR-001…FR-006 (the ship), FR-007 (the caption), FR-008…FR-012 (the
  panels), **FR-013/FR-014 struck** (no insight row, no *What to do next*), FR-015 (the rest of
  three and the tail), FR-016 (the worst panel open at rest), FR-018 (the phone's hoist is a CSS
  `order` off `panel--worst`, never a second DOM order), FR-019 (the foot), **FR-020** (what leaves
  this page), FR-021 (the people line, only while `answered > read`), FR-022 (the hand-off line
  moves to the sheet), FR-023 (the project shell stays), FR-024…FR-030 (the download: three button
  states, five pages, the 16:9 block, the paragraph on page 1, **page 5 names nobody**, the title
  page retired), FR-031/FR-032 (the panel claim). Success criteria **SC-003**, **SC-006**, **SC-008**
  and **SC-009** are the four this repository can read from outside.
- keel-web's **own markup at master `7e5a2a8`**, because what a page object reads is markup and a
  spec that quoted only prose would be guessing at it: `src/routes/founder/OverviewRoute.tsx`,
  `src/routes/founder/PrintRoute.tsx`, `src/components/brief/ShipFigure.tsx`,
  `src/components/brief/StagePanel.tsx`, `src/components/brief/lines.ts`, `src/lib/translate.ts`
  (`PANEL_HELD`, `PANEL_DID_NOT_HOLD`, `TAG_DEAL_BREAKER`, `TAG_WORTH_KNOWING`,
  `panelLinesHolding`, `panelDealBreakers`, `panelPeopleAnswered`, `moreLabel`,
  `moreWorthKnowingLabel`, `shipCaption`, `shipStatusLabel`, `EVERY_LINE_EVERY_ANSWER`,
  `BAND_OPENS_STAGE_LINE`, `DOWNLOAD_PDF_LABEL`, `DOWNLOAD_NOTHING_YET`,
  `DOWNLOAD_NOTHING_YET_HINT`, `DOWNLOAD_PREPARING`, `WHAT_THIS_SAYS_HEADING`, `HANDOFF_LINE`,
  `P169_CAPTION`, `PRINT_EVIDENCE_HEADING`, `PRINT_COL_*`, `PRINT_IN_THEIR_WORDS`,
  `PANEL_SHOWS_CLAIM`), and `src/styles/app.css`'s own `.deck`/`.panel`/`.ship`/`.pages` blocks.
- keel-web `specs/028-phone-shell/` and `specs/029-phone-pages/` — **merged locally, not yet
  deployed.** They keep the deck and add a bottom tab bar on phones. This spec writes selectors that
  survive them and assumes **no phone chrome** in a 1280 × 800 desktop run.
- keel-cloud `canon/openapi-v2.yaml` at this checkout — `Overview` (`stages[].verdict`,
  `peopleAsked`, `peopleAnswered`, `dealBreakersHolding`, `dealBreakersTotal`, `claim`,
  `whatThisSays`, `whatThisSaysNote`), `Standing` (`holdingUp`, `notHoldingUp`, `peopleDisagree`,
  `untested`, `people[].status`, `people[].personName`), `StandingLines`.
- this repository at `master` `736a61e`: `evals/test_s012_journey_through_a_host.py` from §1.6 to
  the end, `harness/browser.py` (`Overview`, `OverviewCard`, `PrintPage`), `harness/rubric.py`,
  `evals/policy.py`, `tests/test_policy_v8.py`, `evals/test_s001_smoke.py`,
  `evals/corpus_scenario.py`, `evals/test_s005_countly.py`, `evals/test_s007_mulchrun.py`,
  `evals/test_s002_agent_optional.py`, `evals/test_s003_every_door.py`,
  `evals/tools/curated_proof_run.py`, `tests/test_page_object_calls_exist.py`,
  `tests/test_journey_coverage.py`, `tests/test_review_card_chips_markup.py` (the shape this
  repeats), `AGENTS.md`.
- **the red run**: the live Lullaby journey, matrix run **36870786241**, against staging keel-cloud
  **782a01a** and keel-web master **7e5a2a8**. It gets all the way through framing, the one
  questionnaire, five invites, the answers and the readings — project at revision **34** — and fails
  at **§1.7 *What this says* — the paragraph the host wrote, unasked***: `Overview.open(project_id)`
  waits thirty seconds for `".ocards, .guided-step"` and times out.
- `.specify/memory/constitution.md` — still an unfilled template at `736a61e`, every principle
  `[PRINCIPLE_N_NAME]`. Recorded because a spec that claims to have been checked against a
  constitution should say when there is nothing to check against. `AGENTS.md` is this repository's
  governing document and is what this spec is written to.

## The one sentence

**The live journey stops waiting for a screen that no longer exists: `Overview.open` waits for the
deck, §1.7 becomes the deck's own assertions — three bands coloured by the verdict the wire sent,
three panels naming their stage and its word, each panel's count line compared number for number
against `GET /overview` and `GET /standing`, the worst panel open at rest, and the download live
exactly when a reading exists — and the *What this says* assertion moves, intact, to page 1 of the
brief, which the journey now opens and reads whole.**

## Why this exists

keel-web spec 027 `brief-ship` replaced the overview with the deck and deployed it. This repository
is the referee, and a referee that waits for a node the product deleted reports *the product hung*
when what happened is *the referee is looking at the wrong screen*. Run 36870786241 spent a whole
live journey — the framing, the questionnaire, five people's answers, five readings and the BRIEF
job — and then said nothing about any of it, because the one page object it needed had an old
selector in it.

Three things make this worth a spec rather than a one-line selector fix.

1. **`.ocards` was not deleted from keel-web.** `StageRoute`'s own opened card still draws it
   (keel-web 027 Discovered D-10), so the wait was not for a removed class but for a live class on
   a different screen — the shape of mistake no grep finds and no type checker catches. The fix has
   to be *the page object is proved against the real deck*, not *the selector is changed and we
   hope*.
2. **Four assertions lost their subject, and none of them may be dropped.** The bar's *N of T lines
   have answers*, the four-count legend, the three stage cards and the paragraph all stood on this
   screen. Three of them have successors on the deck and one has a successor on the sheet. AGENTS.md's
   rule is that an assertion is inverted or moved with its reason written above it, never deleted.
3. **The brief is where the paragraph lives now**, and the journey had never opened the brief at
   all. S-012 asserted the sheet nowhere; S-001 and the corpus scenarios did, through readers that
   `PrintRoute`'s own rewrite broke in two more places (`.ptitle`, and a fourth `table.ptab` on
   page 5). A spec that moved only the paragraph would have left those for the next red run.

## What this is not

- **Not a change to what any rubric check means.** `evals/policy.py` is untouched: no check is
  added, removed or reweighted, `CHECKS` and the four category weights are byte-identical, and
  `RETIRED_STRINGS` gains nothing. Two readers move — GUI-U1's `affordance` and the `what_this_says`
  capture — and the Discovered ledger names both.
- **Not a live run.** Nothing here calls a model, opens a browser against staging or runs
  `make eval-live`. The gates are `make unit` and the offline markup tests.
- **Not the phone.** keel-web specs 028/029 are merged locally and not deployed. The selectors are
  written to survive the tab bar; no assertion is made about it.
- **Not the slide frame, and not a pixel.** keel-web's own SC-001/SC-002/SC-004 (one viewport, one
  scrolling box, the slide test) are measurements in keel-web's browser, taken against keel-web's
  own fixtures. This repository asserts structure and numbers, never layout.

## Requirements

### The page object reads the deck (FR-001 … FR-008)

- **FR-001** `Overview.open` waits for the deck **or** the walk's current step, and no longer for
  `.ocards`. The wait selector is one class constant, `Overview.DECK`, and it lists `.deck`,
  `.ship`, `.panels` and `.guided-step` — the first three because the phone shell may wrap the deck
  in other chrome, the fourth because `OverviewRoute` renders `GuidedStep` instead of the deck while
  any stage is still a draft, which is the state this page object is opened in for most of the
  journey.
- **FR-002** `Overview.is_deck()` says which of the route's two renderings is on the screen, so a
  scenario never re-derives *the framing is done* from the wire to know which assertions apply.
- **FR-003** `Overview.bands()` reads one row per band of the ship, in the figure's own
  top-to-bottom order: `{stage, wash, lit, label, href}`. `stage` is `data-stage`; `wash` is the
  verdict modifier off `band--{good,warn,bad,none}`; `label` is the band link's own `aria-label`,
  which carries the same verdict **in words**, so an assertion over this read passes on a deck
  stripped of every colour.
- **FR-004** `Overview.ship_label()` reads the figure's one accessible name — all three stages and
  their words in one line — and `ship_caption()` / `ship_counts()` read the caption *Countly · 18
  lines · 12 asked* and its two numbers.
- **FR-005** `Overview.panels()` reads one row per panel: `{stage, wash, worst, lit, name, word,
  tone, claim, count, parts}`, where `parts` maps a part's own label to its rows and a row is either
  a line — `{heading, tag, line, pip}` — or that part's tail, `{more}`. **A part with no lines
  renders no `dt`**, so an absent key means *this stage has nothing in that list* and is a finding,
  not a missing node. `Overview.part_of` / `lines_of` / `tail_of` are the three class-level readers
  over it, matching the label case-insensitively because the `dt` is CSS-uppercased.
- **FR-006** `Overview.worst_panel()` reads the `data-stage` of the one `panel--worst`, and
  `open_every_tail()` clicks every *N more ›* until none is left and answers how many it clicked —
  which is how a scenario counts a stage's lines off the screen instead of off the three a closed
  part shows.
- **FR-007** `Overview.download_state()` answers `{label, enabled, href, why}` for both of the
  overview's download states. `enabled` is *has an `href` and is not `aria-disabled`*, because an
  anchor with no `href` navigates nowhere and that is the whole mechanism of the disabled state.
  `Overview.download()` follows the founder's own link and, since it is `target="_blank"`, **answers
  whichever `Page` the sheet landed on**.
- **FR-008** The retired reads are **kept, not deleted**: `evidence_line`, `percent_line`,
  `lines_with_answers`, `legend`, `stage_cards`, `what_this_says`, `what_this_says_paragraph`. Each
  answers empty on the deck — which is a finding a scenario can assert rather than a crash — and
  each one's docstring names the read that succeeded it. `legend_present()` and
  `carries_what_this_says()` stand beside the two whose empty answer is ambiguous, because four
  zeroes is also what a brand-new project would show.

### The page object reads the brief (FR-009 … FR-013)

- **FR-009** `PrintPage.PAGE` is `.pages > .page` and `page_count()` reads it. The sheet is five
  pages in the order **page 1, problem, solution, commercial, evidence** (keel-web SC-008).
- **FR-010** `PrintPage.page_one()` reads page 1 whole — `{kicker, name, sub, meta, handoff,
  caption, what_this_says}` — and **`title_page()` is re-pointed at it**. keel-web FR-030 retired the
  separate title page, so `.ptitle` no longer exists; every assertion made through `title_page()`
  stands where it stood.
- **FR-011** `PrintPage.what_this_says_paragraph()` reads **page 1's own `p.pclaim`, and nothing
  else**. Pages 2–4 each draw a `p.pclaim` too — `StageSummary.claim`, a different field with a
  different author — so a sheet-wide read compares a stage's claim against `Overview.whatThisSays`
  on the wire and fails on a correct product. `what_this_says_heading()` and `what_this_says()`
  stand beside it; `PrintRoute` draws the heading and the paragraph together or neither, and prints
  **no `whatThisSaysNote`** in their place.
- **FR-012** `PrintPage.block_169()` reads the ruled 16:9 block: `{present, caption, bands,
  panels}`. It renders the **same `ShipFigure`** at a different size, so its bands are read the same
  way the deck's are; without a `projectId` the figure is a drawing and says so with `aria-hidden`,
  which is why `bands()` reads the wash off the path and the link only where there is one.
- **FR-013** `PrintPage.table_columns()` is **scoped to the stage pages**, and
  `evidence_page()` reads page 5: `{heading, lede, columns, rows, names, quotes}`. Page 5's evidence
  table is a `table.ptab` too (keel-web FR-029), so the sheet-wide read this had answers four rows
  now and the fourth's columns are the evidence page's own four — a caller's assertion failing on a
  correct product. `participant_names()` reads every name the sheet prints beside a quotation, over
  all five pages; `evidence_page()["names"]` is the scoped read page 5 must answer empty.

### §1.7 of the live journey becomes the deck (FR-014 … FR-020)

- **FR-014** Before a single person is invited — every stage approved, so the route renders the
  deck, and nobody asked, so nothing is read — the journey asserts the deck stands and **the
  download is the disabled *Nothing to hand over yet* control with its why beside it** (keel-web
  FR-025 state 3). This is the only moment that state can be read: one reading later it is gone for
  the rest of the project's life.
- **FR-015** The *What this says* step keeps its poll of the wire verbatim — keel-cloud starts the
  BRIEF job by itself when a reading batch finishes, so the founder is given nothing to wait on —
  and keeps `assert paragraph and paragraph.strip()`. **The screen half of it moves** to the sheet,
  where the paragraph is drawn, and is asserted there as byte equality against the same wire value.
- **FR-016** Three bands, each with a verdict class; three panels, each naming its stage and its
  status word. The wash a stage's band must carry is derived from the verdict `GET /overview` sent,
  through keel-web's own `measuredStatus`+`washOf` mapping restated in Python. **The word is
  asserted as well as the wash**, so a deck that lost every colour would still pass.
- **FR-017** Each stage's `panel__count` is compared against the wire, number for number: *N of M
  lines holding* against `GET /standing`'s four lists filtered to that stage, the deal-breaker clause
  against `dealBreakersHolding`/`dealBreakersTotal` (absent entirely where the total is zero, which
  is keel-web's own edge case), and **the counted people** against `peopleAnswered`. Each panel with
  lines on the wire shows at least one HELD or DID NOT HOLD row. **Nothing is recomputed**: every
  number is a field the wire sent or a plain count over a list it sent.
- **FR-018** The worst stage's panel is the one keel-web marked `panel--worst` **and** the one open
  at rest. *Worst* is the verdict order the wire's own verdicts fall into —
  `CONTRADICTED` → `MIXED` → `UNTESTED` → `SUPPORTED`, a tie going to the deepest band — and *open*
  is read as **no tail**, because a tail renders only behind the three a closed part shows.
- **FR-019** With a reading on the wire, *Download the brief* is live and points at
  `/p/{id}/print`. The `READ` count is read off `Standing.people` first, so a step that would
  otherwise be measuring the wrong thing says so.
- **FR-020** The journey then **opens the brief, in this same context, by URL, with `window.print`
  stubbed**, and asserts: five pages; no founder chrome; page 1 headed with the project's name,
  carrying the paragraph under its own heading **byte-identical to the wire**, and carrying the 16:9
  block with three bands, three panels and its caption; and page 5 carrying one row per line on the
  wire, its four named columns, and **nobody's name** — neither in a cell nor as an *In their
  words* block (keel-web SC-009, principle P8). The named quotes stay on the stage pages, and that
  is recorded beside it.

### The sweep (FR-021 … FR-025)

- **FR-021** `evals/test_s001_smoke.py`: the pre-reading *What this says* step is **inverted** — the
  wire still carries no paragraph and still composes its own note, and the screen's statement of
  *there is nothing yet* is the download's disabled state, because the sheet prints no note. The bar
  and legend steps become the deck's; the paragraph step moves to §1.10, after the sheet is open;
  the stage-cards step becomes the panels'. Every assertion stands, somewhere, with the reason above
  it.
- **FR-022** `evals/corpus_scenario.py`: the same four moves, in the shared scenario the three
  corpus entries run through. `_assert_overview` reads the deck; `_assert_no_paragraph_yet` is
  inverted; `_assert_what_this_says` is handed the `PrintPage` instead of the `Overview` and is
  called after the sheet is open; `_assert_download` gains page 1's paragraph position and page 5's
  no-names rule. `expected_legend` is kept and **is read from the wire's standings**, which is where
  it always came from, and compared against the panels' rows rather than against a legend.
- **FR-023** `evals/test_s005_countly.py`'s mockup-of-record step keeps **every number** — Countly's
  9 holding up, 3 not holding up, 6 people disagree, 0 not asked yet, and 18 lines — and reads them
  off what the deck shows: the three panels' HELD rows sum to the first, their DID NOT HOLD rows sum
  to the second and third together, and the caption's line count is the fifth. The one count the
  deck draws nowhere — *not asked yet* — is asserted against the wire, with the reason written above
  it.
- **FR-024** `evals/test_s007_mulchrun.py`'s *no metric unit reaches a founder screen* sweep reads
  the deck's own text (the caption, every panel's word, claim and count line, and the foot) and the
  printed paragraph, which between them cover strictly more than the three strings it swept before.
- **FR-025** `evals/tools/curated_proof_run.py`'s overview and download blocks read the new
  readers. It is a tool and not a scenario, and is fixed because a tool that crashes on the current
  product is debt nobody sees until they reach for it.

### What is proved offline (FR-026 … FR-028)

- **FR-026** `tests/test_journey_brief_ship_markup.py` (new) drives keel-web's **own markup** —
  condensed from `OverviewRoute.tsx`, `StagePanel.tsx`, `ShipFigure.tsx` and `PrintRoute.tsx` at
  master `7e5a2a8` — through `Overview` and `PrintPage` in a real Playwright page, the way
  `tests/test_review_card_chips_markup.py` does. No live run, no stack, no model call.
- **FR-027** It includes **the red run reproduced**: `wait_for_selector(".ocards, .guided-step")` on
  the deck, asserted to raise, so the one-line regression that cost run 36870786241 cannot be put
  back by accident.
- **FR-028** It includes the two scope traps as their own cases: the paragraph reader on a sheet
  whose page 1 has no paragraph but whose stage pages have three claims, and the stage-table reader
  on a sheet with four `table.ptab`.

## Success criteria

- **SC-001** `make unit` is green at every commit on this branch. Baseline at `736a61e`: **1,262
  passed**.
- **SC-002** The red run's own failure is reproduced offline and then made impossible: a test asserts
  the old wait times out on the deck, and `Overview.DECK` is asserted to match it.
- **SC-003** **No assertion is deleted.** Every assertion that stood in §1.7, in S-001's §1.7/§1.10,
  in `corpus_scenario` and in S-005's mockup step either stands where it stood or stands somewhere
  else with the reason written above it. Counted and listed in `tasks.md`.
- **SC-004** Every number §1.7 asserts about the deck is compared against `GET
  /v2/projects/{id}/overview` or `GET /v2/projects/{id}/standing`. **Zero** numbers are recomputed
  from anything else, and the referee decides no verdict, median or standing.
- **SC-005** `evals/policy.py` is byte-identical: no check added, removed or reweighted, and
  `RETIRED_STRINGS` unchanged. `tests/test_policy_v8.py`, `test_policy_v9.py` and `test_policy_v10.py`
  pass untouched.
- **SC-006** `tests/test_page_object_calls_exist.py` passes: every page-object attribute any scenario
  names exists on the class it names it on.
- **SC-007** `tests/test_journey_coverage.py` passes: **§1.7** is still cited in
  `evals/test_s012_journey_through_a_host.py` beside the assertions that enforce it.
- **SC-008** The page objects are proved against the real deck and the real sheet **before any live
  run**: the markup tests cover the bands, the panels' two parts, the tails, the worst panel, both
  download states, every retired reader's empty answer, the five pages, page 1's paragraph and its
  scope, the stage tables and page 5's two no-name shapes.

## The next live run

Nothing on this branch spends anything. The command below is the founder's to type, against a
staging twin carrying keel-cloud **782a01a** or later and keel-web master **7e5a2a8** or later.

```
make eval-live K=s012 HOST=claude LEGS=full ENTRY=03-lullaby PEOPLE=5 PROFILE=remote
```

…or, as the matrix dispatches it, the `nightly` set's own `macos-15-claude-py3.13` cell with
`KEEL_JOURNEY_LEGS=full`. The dispatch inputs are in `tasks.md`'s *The next live run* section, which
is where a reader looking for the command will look.

## Out of scope, named

- **The ORI-U4 `asked_first()` item** from spec 026's Discovered **D-6** stays open. It reads
  `ReviewCard.asked_first()` — a **different page object, on a different screen** (`StageRoute`'s
  draft review card, whose `<dl class="qa">` keel-web spec 026 FR-011 deleted) — and nothing on this
  branch touches it. Named here so the debt stays visible, not discharged.
- The phone shell's tab bar (keel-web 028/029), which is merged locally and not deployed.
- keel-web's own layout measurements (SC-001/SC-002/SC-004 there), which are pixels in keel-web's
  browser against keel-web's fixtures.
- The BRIEF paragraph's four marks — `shape` (no raw stage label), `coverage` (the deciding line's
  number), `register` (second person, the market's own currency) and `source_material`. They live in
  `instructions/brief.py` under `MARKS_VERSION`, are applied to a model's answer and not to a
  screen, and this repository's rule is that the instruction eval never reads `evals/policy.py` and
  the reverse. Recorded in `tasks.md` **D-7**.
