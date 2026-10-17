# Spec 052 -- The report, as the eval sees it

keel-cloud 104 (`StandingsView.priceMedian`, `pilotPeople[]`, `insights[]` from the themes job; the BRIEF job,
`brief.md` and `BriefReading` deleted) and keel-web 077 (the Overview route's three views -- Overview, Insights,
Pilot -- and *Download the brief* as the binding; the old brief routes and deck pieces removed). Design of record:
keel-cloud-docs `canon/designs/report-and-follow-up-design-2026-10-17.md` §3, §4, §7, §11. **Contract 19**, the
standings side. Selectors are the design's words; where 077 settles one it is marked *as 077 defines*.

## Rules

- **FR-1 The reading marks retire.** `instructions/brief.py` (the seven reading marks and `brief_answers`),
  `instructions/marks.py`'s `brief_answers` row, `evals/corpus_scenario.py` `leg_brief`'s reading half and
  `_brief_pages`, `tests/test_instruction_brief_reading.py`, `rescore.py`'s BRIEF handling: deleted, not skipped.
  `brief_facts` **stays** (the card lines are the one source, design §3) and gains the two project numbers:
  `pilot` as today and `priceMedian` (`{edgeSaid, chose, n}` or absent) computed by `instructions/brief_facts.py`
  from the entry's price table the way the design says (the highest edge with `chose * 2 >= n`). Two card lines
  move with 104: Compatibility's could-phrase and Purchase friction counting supporters -- `brief_facts` reads the
  registry export for the words, as it does today. **`MARKS_VERSION` 19 -> 20**, the history paragraph written.
- **FR-2 The themes fake**, one source with keel-cloud 104's: groups a dimension's follow-up answers by their
  first noun (lower-cased, stop-words skipped), at most three piles by count, label = that noun; mirrored in
  `harness/interviewer_fake.py` (`themes(answers)`) so the eval can predict the Insights tab word for word from the
  people's `follow_up` lines (051 FR-11). Held to 104's `FakeThemes` by a unit test over the export, as the ladder.
- **FR-3 The Overview** (`harness/vectors_screens.py` `Answers.board`, rewritten for 077): the hero (`.verdict`
  text and its `l-{label}` class; the one line under it; the ship's three `path.band` classes), the two tiles
  (`.tile--pilot` and the price tile, *as 077 defines*: big and line), the three panels (name, pill, lead line, every
  row's name / status word / number line or *nobody has answered this yet*, its href), the foot. Marks:
  - **`report_overview`** (corpus, `DRY=1`-measurable like `brief_facts`): every row equals the card the wire
    serves (`StandingsView` cards: `number`, `line`, the status word = the first part of `statusWords`), in the
    registry's order within its stage; the verdict word is `SHIP[label]` and how sure `SURE[howSure]`; the panels'
    lead lines follow design §4.1 (3) by status; the pilot tile reads `k of n signed up · p% · per link` or *None
    yet*; the price tile reads `{edgeSaid} or more · half or more said so · {chose} of {n} decision-makers` or *Not
    asked yet · no decision-maker has answered the money questions*; on KEEP_INTERVIEWING the under-line is
    *{n} people have answered.* with the *Send the questions to more people ›* link to Interviews.
  - a plain assertion: nothing from the old deck -- no `p.overall`, no people tile, no `.snaprow`, no
    `.panel__count`, no *A band opens its stage*, no disabled download.
- **FR-4 The Insights view** (`Answers.insights`, the segmented control *as 077 defines*): per dimension not
  holding, worst first, the box: heading = the dimension's name, the pill, the rung's heading (the eight of design
  §4.2 with *· {answered} of the {against} said why*), the themes as the fake predicts (label, count, up to three
  quotes each ending `— {Name}`, the name the invitation carries), the *Only k of the n were asked here…* line where
  the people's rungs say so, *No follow-up on this rung: …* on a rung without a question, the split line on
  PEOPLE_DISAGREE; the two empty states word for word. Marks:
  - **`report_insights`**: the boxes equal the prediction from the standings (which dimensions, order, headings,
    themes from `insights[]` with the fake, names resolved, counts summing to `answered`); the empty state is the
    right one of the two.
  - **`report_no_repeat`** (design D6, a literal check): no token of the form `\d+ of \d+`, no `£\d`, no
    `\d+ months? out of`, and none of the Overview's card `number` strings appears anywhere in the Insights view's
    text, except inside a quote (`.qt`) and the *k of the n said why* / *Only k of the n* lines, which are the
    tab's own.
- **FR-5 The Pilot view** (`Answers.pilot`): the pilot tile, the *What they agreed to* tile, one row per person
  with name, role words, source, email where the link carried one, and inside: gate, story, every answer as
  *dimension → words*, the follow-up (rung and words). Mark **`report_pilot`**: the rows equal `StandingsView.pilotPeople[]`
  and that equals the people the walks opted in (051's and 044's `pilot_opt_in` stand-in); emails only where the
  invitation had one (dataset links); *Nobody has signed up yet.* before any opt-in; *Keel never emails on your
  behalf…* present.
- **FR-6 The binding** (`Answers.brief(printed=True)` rewritten; the old `brief` and `breakdown` readers deleted):
  `/p/{id}/print` is pages 1..n: page 1 the Overview inside the 16:9 block (the hero, the tiles, the panels' lead
  lines, **no rows**), page 2 the Insights view, page 3 the Pilot view, then the breakdown tables (one per stage:
  dimension · card · answers · status; the price table with the median line). Mark **`report_binding`** (design D10):
  for each of pages 1–3, the page's text tokens (words of 4+ letters and every number) are a subset of the
  corresponding view's text tokens plus the page frame (kicker, title, meta line, footer); the breakdown's tokens a
  subset of the stage pages' and the standings' (every number on it is a count in `StandingsView`); and the sheet
  carries **no** `headline`, no *What to do next*, no *In their words* heading on a healthy project (D9). Title as the
  file name (`<project> — Keel brief — <date>`), *Preparing your brief…* then the pages (050's `window.print` stub).
- **FR-7 The healthy journey**: a new scenario `test_s014_green.py` on the corpus entry whose standings all hold on
  n >= 10 (pick it from `export/`; if none, build it from `05-paidly` with every person supporting, as the cloud's
  `InsightsSimulationTest` baseline does): no person is owed a follow-up (051 IM23's none case on both links), the
  Insights view is *Nothing is failing*, the Pilot view lists the opt-ins, the binding ends after page 3's tile line
  and the breakdown; `report_no_repeat` and `report_binding` hold. Also the too-few state on S-005 before the fifth
  answer (`_board_tiles(... "before anyone answered")` widened): *Keep interviewing*, *Nothing to read into yet*,
  *Not asked yet* on the price tile, *nobody has answered this yet* on every commercial row.
- **FR-8 S-005 / S-006 / S-007** read the three views and the binding after every answer lands, in place of
  `leg_brief`'s pages; the stage-page reader (`vector_page`) gains the per-person follow-up line (*One last thing ·
  {rung}: "…"*) and asserts it for the people who answered one.
- **FR-9 The facts' quotes.** `instructions/brief_facts.py` learns nothing about themes (they are the model's) --
  the eval predicts them through the fake only on the stack; on the live cell the Insights view is asserted for
  shape (≤ 3 themes, counts summing, every quote a verbatim follow-up line of a named person, the name the one on
  the invitation) and never for the labels. A label check on the live cell is out of scope.

## Acceptance

1. `make unit` green: the retired tests gone, the new marks each with a seeded fault, `priceMedian` on a hand-worked
   price table (three edges, the half rule at an exact half), the themes fake held to 104's, `report_no_repeat` on a
   seeded repeat; count in tasks.md (2,391 / 53 before; 051 lands first, so measure against its number).
2. `make eval K="s005 or s006 or s007 or s014"` green on a fresh stack against keel-cloud 104 + keel-web 077 after
   051 + 076; the four new corpus marks measured and met on S-006 and S-014; the too-few state on S-005.
3. Remote journeys green on staging; DRIFT entries for what the page shows that the wire does not say, and for any
   number the Insights view repeats (expected: the first builds of 077 will repeat one -- #93 reserved for it).

## Judgement calls (decide, document in tasks.md, do not ask)

1. Which entry is the healthy one (prefer a real corpus entry over a built one; say which).
2. Whether `report_binding` compares tokens or normalised sentences (prefer tokens: CSS case and line breaks differ
   between a tab and a sheet).
3. The marks' names and `MARKS_VERSION` 20's history paragraph.
