# Tasks 090 -- The harness walks the money screens as keel-web 134 draws them, the three controls as keel-web 135 builds them, the five 0s sent as 1, and Send more's words as keel-web 130 draws them

Branch `090-and-093-the-screens-as-drawn` (worktree `wt/eval-090`, `.git` a file), off master `242f289`, with spec 093
on top of it on the same branch (`specs/093-the-phrase-is-the-peoples-mirror/tasks.md`). Built by Claude Opus 5.5 on
2026-10-30 (the hand-off named `Claude Fable 5.1` for the commit trailer, and the commits carry it). Read only, the live
checkouts `stack.toml` points at: keel-cloud-docs master **`a396fe9f`** (149-163 in; contract 48; corpus revision 19)
and keel-web master **`02b952c`** (129-135, 138, 139 in; vendored contract 47). Inputs: the spec of record (FR-1 to
FR-5, not edited); keel-web 134's tasks.md (the cost box's ids and order, the six price choices), keel-web 135's tasks.md
(the harness list, H-1 to H-16), keel-web 130's tasks.md (the five founder screens' words), keel-web's `translate.ts`,
`lib/costLine.ts`, `FounderControl.tsx`, `BeforeStep.tsx`, `SendMorePopup.tsx` and `aiInterviewFlow.ts` read to confirm
each id and word; this repo's 089 tasks.md and AGENTS.md. **No paid call**: no `make eval`, no `make instruction-screen`
beyond `DRY=1`, no `make quality-*`, no model, no reader. Nothing merged or deployed; the branch pushed after every
commit. The journeys (`make eval K=s005` / `s006` / `s007` / `s012`) are the coordinator's, on the stack after the
merge.

| Commit | What |
|---|---|
| `7d9e7a8` | FR-1: the money screens -- the mode first, the composed line, *A share they lose*, the six named price choices |
| `39da8d3` | FR-2: the three controls as 135 builds them -- H-1 to H-9 mirrored |
| `47f5c49` | FR-3: the five recorded 0s sent as the count 1 |
| `f9b3500` | FR-4: Send more's words and the founder screens' words (keel-web 130) |
| (093's five commits) | spec 093 |
| the docs commit | this file, 093's, `AGENTS.md`'s spec-090 and spec-093 paragraphs |

## Unit (the gate)

`make unit`, against the live checkouts above (keel-cloud-docs `a396fe9f`, keel-web `02b952c`):

| | passed | failed | skipped |
|---|---|---|---|
| master `242f289` | 3,773 | **3** | 55 |
| branch at 093 FR-3 (`67d6e9b`) | 3,841 | 0 | 53 |
| **branch, final tree (the docs commit; 093 FR-5 `1083f7a` is the last code)** | **3,855** | **0** | **53** |

Master's three reds on these checkouts: `test_controls_089.py::test_the_registrys_lullaby_examples_are_the_frames_the_harness_composes`
(161 wrote the Lullaby phrase bare -- 093 FR-1), `test_controls_089.py::test_the_five_zeros_are_held_for_the_founder_and_158_159_are_marked_merged`
(the founder decided D-2026-10-30-01 on 2026-10-30: `taken` -- this spec's FR-3) and
`test_follow_up_ladder.py::test_the_composers_defaults_and_its_one_more_thing` (161's `{phrase}` default -- 093 FR-2).
All three are green on the branch. The handoff's *3,776 / 55* (the spec's acceptance line) was 089's count on the cloud
before 161: 3,773 + 3 is the same 3,776 tests. The branch's two fewer skips are the ladder's registry tests
(`test_the_ladder_is_the_registrys_own`, `test_each_texts_placeholders_are_the_registrys_and_fill_knows_them`), which
skipped by mistake on a 161 registry and run again (093 FR-2).

## FR-1 -- the money screens (keel-web 134) -- `7d9e7a8`

- [x] T001 `harness/vectors_screens.py` `Corridor._chain_cost`: reads the page's line `chain-cost-line` (`line`) and what
  of *Per* (`chain-unit`) and the period chips (`CHAIN_PERIOD_CHIPS`: `[data-testid^=chain-period-]` but not
  `chain-period-label`) is on the page **before** the mode (`before_mode`, owed `{unit: 0, periods: 0}`); clicks the
  mode; waits for `chain-unit`; reads *Per* and `#chain-unit-help` as they arrive filled; fills the unit, clicks the
  period chip, waits for `chain-equation`, reads *of* and on hours the rate as before. The frame returned carries
  `order: "mode-first"`.
- [x] T002 `CHAIN_MODE_WORD["RATE"]` *A share they lose* (was *A rate they lose*). `CHAIN_COST_HOW` stays the neither-part
  form; `cost_how_line(payer, core)` is keel-web's `costHowLine` (the four forms); `cost_line_parts(b2b, context, base)`
  is `costPayer` (*the buyer's organisation*, `COST_PAYER_B2B`, on a B2B study; else the context's `segment.core` as a
  sentence takes it) and `costCore` on a fresh draft (*each {occasion}*, the occasion the *of* box arrives with --
  `corpus_scenario.chain_fill`'s `base`, which is keel-web's `occasionBase`).
- [x] T003 `evals/corpus_scenario.py` `_hold_the_mode_first` (called from `_hold_the_chain_screen` when the frame says
  `mode-first`): nothing of *Per* or the periods before the mode; the line in the shape the served parts allow
  (`cost_line_owed`: *How would you put the cost of ... to ...?* with both, the shorter forms with one, `CHAIN_COST_HOW`
  with neither); never the context's circumstance; exactly the composed line on a strict journey.
- [x] T004 `Corridor._chain_price`: one click on the choice's own id (`chain_price_choice`, `CHAIN_PRICE_CHOICE`):
  `chain-shape-AMOUNT_PERIOD`; SHARE on the cost's base `chain-shape-SHARE` alone (**`chain-share-COST_BASE` is gone**);
  RECOVERED `chain-share-RECOVERED`; UPFRONT_THEN with a fee `chain-shape-UPFRONT_THEN`, with nothing more
  `chain-then-nothing`; FREE `chain-shape-FREE`; then the numbers (`chain-price-low/high`, `chain-share`,
  `chain-upfront`, `chain-plan`) and the locked words read back as before; the frame records `choice`.
- [x] T005 Tests: `tests/test_screens_as_drawn_090.py` (FR-1: the modes, the four line forms, the parts, the six
  choices clicked once each with their numbers, the hold taking the composed line and failing the old order, the old
  line and the circumstance, the shorter forms without a context).

### Pins moved (FR-1)

| File | Old | New | Why |
|---|---|---|---|
| `harness/vectors_screens.py` `CHAIN_MODE_WORD` (109) | `"RATE": "A rate they lose"` | `"A share they lose"` | 134 `CHAIN_COST_MODE_WORD` |
| `harness/vectors_screens.py` `_chain_cost` (1556-1607) | *Per* and `#chain-unit-help` read before the mode click | the mode clicked first; *Per* read after it is drawn; `before_mode`, `line`, `order` recorded | 134 T001-T002: nothing but the modes before a pick |
| `harness/vectors_screens.py` `_chain_price` (1609-1626) | `chain-shape-{shape}` then `chain-share-{base or COST_BASE}`; `chain-then-nothing` after the shape | one click on the choice's id; no `chain-share-COST_BASE` | 134 T007, J-4 |
| `harness/vectors_screens.py` `CHAIN_COST_HOW` (108) | the cost box's one line | the neither-part form of `cost_how_line` | 134 T003 |
| `tests/test_backtest_scope_082.py` `_ChainPage` | *Per* and the periods drawn from the start; the equation once mode, unit and period | the line and the modes alone; *Per*, the periods, the equation (and *of*, the rate) once a mode is picked; `chain-per` once unit and period | 134's build |
| `tests/test_backtest_scope_082.py` `test_the_of_box_is_read_after_the_period_once_the_equation_is_drawn` | read *Per* < press mode < press period | press mode < read *Per* < press period; `before_mode` none; the line read | 134 T002 |

No founder-walk recording or fixture in this repository pins the chain's words or ids (searched: `A rate they lose`,
`chain-share-COST_BASE`, `How would you put`, `COST_BASE`): `quality/scores/*` quote *A rate they lose* as a reader's
words about an old screen -- a record, not a pin, left as written.

## FR-2 -- the three controls as keel-web 135 builds them -- `39da8d3`

keel-web 135's harness list, item by item:

| Item | What the harness did | What it does now |
|---|---|---|
| **H-1** the AI sheet's second ask | `more_said` from `.iv-q` + `ai-status`; the loop guard and `_wait_next` read `vs.ONE_MORE` in `.iv-q` | `Player.second_ask()` reads `[data-testid=ai-sheet] [data-testid=second-ask]`; `more_said` is it equal to the served `secondAsk.question`; the guard and `_wait_next` compare the item's own question alone; *Nothing else* is the served `secondAsk.escape.label` (registry's where none) |
| **H-2** IM20's phase | `one` read 1.5 s after the first tap, while the `more` clip may still play (`speaking`) | `at_tap_wait` keeps the 1.5 s read; `one` is read after the clip has played and the stage is `listening`; IM20 reads `one` as before (`INTERVIEWER_MARKS_VERSION` 14 stands: the reading did not move, the moment of the read did) |
| **H-3** one pick + NOTHING_ELSE on the AI link | `answer()` took `ans["chip"]` first and tapped the first chip (*None of these*) | Importance with `optionIds` is taken before the escape: the first-by-taps walk taps the pick then *Nothing else*; the escape branch is reached only by an answer with no picks |
| **H-4** one pick by speech | said one label, then waited for a next question that never came | `_Walk.one_by_speech`: the label said and held, the `second-ask` line waited for, *Nothing else* tapped, `how` TAPPED (keel-web's `takeSecond` keeps the spoken pick in `heard`); two picks still said together (H-15) |
| **H-5** the hint | held *Pick two.* on `pick_two` alone | `corpus_scenario.PICK_ONE_HINTED` = `pick_one_then_one`, `scale_four`, held to `IV_PICK_ONE` *Pick one.*; `IV_PICK_TWO` removed |
| **H-6** *2 of 2 picked* | read from the first ask's record (always "") | `_one_then_one` reads `.iv-picked` after the second tap into the second ask's record (`picked_line`); recorded, not held (judgement call 3) |
| **H-7** the pressed *Nothing else* | not read | `_one_then_one` reads `.iv-chips button[aria-pressed=true]` (`pressed`); the AI walk's `two.pressed` from `Player.chip_pressed()`; recorded, not held |
| **H-8** dead `pick_two` paths | `PICK_CONTROLS`, `ROW_CONTROLS`, `PICKS_NEEDED` carried `pick_two`; `_answer`'s checkbox role; the module note *tapped checkboxes wait for Save and next* | gone from the walks and the corpus scenario; `_answer`'s rows are radios; the note says why it no longer applies. `harness/classifier_guard.py` keeps `pick_two` (it reads keel-cloud's recorded classifier cases, judgement call 4) |
| **H-9** the wire's advantages | `gallery._item` and `backtest.served_items` wrote `advantages: []` for every item | read only where a recording made before contract 47 served them (never an empty list); the gallery's pinned interview loses its eleven empty lists; `backtest`'s report keeps reading a recorded bundle's `advantages`. `harness/classifier_cases.py` and `evals/noise/dataset.py` keep their pre-159 Relative advantage options: they are keel-cloud's classifier cases, not the web's (named for the sweep, not moved: FR-5) |
| **H-10** Frequency on the text page | radio by its number | confirmed: unchanged (the 0s are 1 now, FR-3) |
| **H-11** Importance on the text page | the wait for the served `secondAsk.question` by exact text | the wait is on `get_by_test_id("second-ask")` (the sturdier read 135 names); its text recorded as `prompt` and held to the served question as before |
| **H-12** *None of these* before the first tap | clicked by label | confirmed |
| **H-13** Relative advantage | one radio by its served label | confirmed (`ROW_CONTROLS` has `scale_four`; *Pick one.* now held over it, H-5) |
| **H-14** Importance on the AI sheet by taps | `p.tap`, `tap_chip_named`, the `more` clip, no `ai-save` | confirmed |
| **H-15** two named at once | `held(" and ".join(two))` | confirmed (now only when two are named) |
| **H-16** the number range | *31* a miss | confirmed |

- [x] T006 `harness/interviewer_screens.py`: `Player.second_ask()`, `Player.chip_pressed()`; the module note.
- [x] T007 `evals/interviewer_leg.py`: `PICK_CONTROLS` = `("pick_one_then_one",)`; `_wait_next`; `tap_one_then_one`
  (H-1, H-2, served *Nothing else*); `answer()` (H-3, H-4); `one_by_speech` (new).
- [x] T008 `harness/vectors_screens.py`: `IV_PICK_ONE`; `_one_then_one` (H-6, H-7, H-11); `_answer`'s radio rows.
- [x] T009 `evals/corpus_scenario.py`: `ROW_CONTROLS`, `PICK_ONE_HINTED`, `PICKS_NEEDED` (H-5, H-8).
- [x] T010 `evals/gallery.py`, `evals/backtest.py` (H-9); `evals/interviewer_marks.py` IM20's docstring (H-2).
- [x] T011 Tests: `tests/test_screens_as_drawn_090.py` (H-1 to H-9 each by source order or by value).

### Pins moved (FR-2)

| File | Old | New | Why |
|---|---|---|---|
| `tests/test_controls_089.py::test_the_screens_tap_one_wait_for_the_second_ask_then_the_other` | the wait at `get_by_text(prompt, exact=True)` | at `get_by_test_id("second-ask")` | H-11 |
| `tests/test_controls_089.py::test_the_ai_link_taps_one_hears_and_one_more_then_the_second` | `p.tap_chip_named(vs.NOTHING_ELSE_LABEL)` | `p.tap_chip_named(nothing)`, the registry's label where none is served | H-1 (the served label) |
| `tests/test_journey_through_a_host.py::test_a_pick_the_page_does_not_offer_is_named_never_swapped` | Importance as `pick_two`: one of two kept goes to the escape | as `pick_one_then_one`: kept with `chip: NOTHING_ELSE`; the scale with none still to the escape | H-8: contract 47 serves no `pick_two` |
| `tests/test_gallery.py` / `tests/fixtures/gallery/expected-interview-fresco.json` | eleven items with `"advantages": []` | none; the Relative advantage item's recorded two benefits kept | H-9 |

## FR-3 -- the five 0s sent as 1 -- `47f5c49`

- [x] T012 `harness/vectors_script.py`: `ZERO_AS_CANT_RECALL` -> **`ZERO_SENT_AS_ONE`** (the same five, the same windows:
  04-linerly Bruno Costa, Dmitri Volkov, Gwen Price, 12 MONTHS; 05-paidly Petra Novak, Talia Ben-David, 3 MONTHS);
  `_frequency_from_one` sends `scale=FREQUENCY_MIN` (1) in place of the escape -- `{"scale": 1}` on the wire, 1 on the
  segmented control or in the number box, as every other count those people send; `zero_note` says *... recorded
  problem.frequency 0 after a yes; keel-cloud 158 counts from 1, so the walk sends 1 (the founder's D-2026-10-30-01: a
  yes followed by a count of 1 is the floor) -- the corpus is unchanged*; `FREQUENCY_ESCAPE` removed. Each note still
  reaches the journey's findings (`corpus_scenario`, unchanged but for its comment).
- [x] T013 `tests/test_controls_089.py`: the five-exactly test reads `scale == 1` and `{"scale": 1}` on the wire; the
  any-zero test sends 1; the decision test reads D-2026-10-30-01 as the founder left it (`taken`, `spec-merged`, its spec
  *keel-e2e-eval 090 FR-3*, *sends 1* in its why) and takes it with or without the `merged` mark the coordinator adds.
  `quality/decisions.toml` is not edited.

## FR-4 -- Send more's words and the founder screens' words (keel-web 130) -- `f9b3500`

| File / name | Old | New | Why |
|---|---|---|---|
| `harness/interviews_screens.py` `WHO_OWN` (102) | *Someone I know* | *People I know by name* | 130 `SEND_WHO.OWN` |
| `harness/interviews_screens.py` `WHO_DATASET` (103) | *People from a dataset* | *People I found with Keel* | 130 `SEND_WHO.DATASET` (held by `contacts_leg`) |
| `harness/interviews_screens.py` `send_someone` (479) | `rf"^{WHO_OWN}"` | `rf"^{re.escape(WHO_OWN)}"` | the radio's name opens on the label, its line after |
| `harness/vectors_screens.py` `PERSONA_QUESTION` | *Who makes the buying decision?* (exact) | the shape *Would {actor} decide to use and pay for {idea}, or would someone else?* (regex) | 130 `personaQuestion` names the WHO and the idea |
| `harness/vectors_screens.py` `PERSONA_SAME` | *The same person would decide to pay* | *{Actor} decides* / *decide* (regex, never *Someone else*) | 130 `personaSame` |
| `harness/vectors_screens.py` `PERSONA_SOMEONE_ELSE` | *Someone else would decide* | *Someone else decides* | 130 |
| `harness/vectors_screens.py` `L1_TITLE` | *Who asks the questions* | *Who should ask them your questions?*, and `l1_title(people)` *Who should ask {people} your questions?* within ten words | 130 `beforeInterviewerTitle` |
| `harness/vectors_screens.py` `BEFORE_LOCK_RECORD` | *Lock and record the interviewer* | `^Lock and record \S.*$`, `before_lock_record(face)` | 130 `beforeLockRecord` |
| `harness/vectors_screens.py` `BEFORE_LOCK_APPROVE` | *Lock and approve* | *Lock and write the questions* | 130 |
| `harness/vectors_screens.py` `BEFORE_INTERVIEWER_OWN` | *The AI interviewer needs Keel's credits; links go out as text.* | *This account runs on its own AI, so people read the questions and tap their answers. The AI interviewer needs Keel's credits.* | 130 |
| `harness/vectors_screens.py` `PILOT_TITLE` (new), `word_pilot_and_lock` | the pilot screen's title not read | *Offer a pilot?*, read into `ready["pilot_title"]` and recorded by `_keels_door_l1` | 130 FR-3 |
| `evals/corpus_scenario.py` `_keels_door_l1`, `_own_door_l1` | title held to *Who asks the questions* | held to `l1_title_owed(j)` (the context's people) | 130 FR-2 |
| `evals/backtest.py` the describers (1000, 1004) | *Lock and record the interviewer ...*, *Someone I know: ...* | *Lock and record the face Keel preselects*, *People I know by name: ...* | 130's words |

The format rows were checked against 130: their names (*Text only*, *AI interviewer · {face}*, *Let them choose*) and
greyed words did not move (130 moved their lines and added `format-credits`, which the harness does not read). The list
label (*List · {kind} only · {n}*, *Choose a list*) is not read: the harness reads the chosen option's text, a list's
name. `tests/test_screens_as_drawn_090.py` holds every word above and the two L1 holds.

## FR-5 -- nothing else moves

The corpus (revision 19), the readers, the quality cycle's rubric, the prices (088), the frames (089 FR-5): untouched.
No mark moved for 090 (`INTERVIEWER_MARKS_VERSION` 14; `MARKS_VERSION` moved in 093, for 093's reasons).

## Judgement calls

1. **The cost line is held by shape, and exactly only on a strict journey.** FR-1 says the line *where both parts are
   served, the shorter forms where not*: the shape follows the parts the wire serves (`cost_line_owed`), and a strict
   journey (the golden walk) also holds the exact composition. The core is the occasion, never a stored base: every
   walk opens the cost box fresh.
2. **`before_mode` counts the period chips, not their label**, by `:not([data-testid=chain-period-label])` -- the label
   shares the chips' prefix.
3. **H-6 and H-7 are recorded, not held.** The line and the pressed state are read right after a click the page then
   answers; holding them would make the journey wait on a render the harness has no need to gate on. 135 says *if the
   line is wanted*.
4. **`classifier_guard.PICK_CONTROLS` keeps `pick_two`.** It sorts keel-cloud's recorded classifier cases (and a
   pre-46 link a recorded run may hold), not a screen of contract 47; the walks and the scenario drop it (H-8).
5. **H-9 reads a recorded run's benefits, not an empty list.** The gallery exports recorded runs (its pinned one is
   pre-47): `advantages` is written only where the recording served some, so a contract-47 item carries no such key and
   the old run keeps its own words.
6. **One pick by speech ends on a tapped *Nothing else*** (H-4 says *say or tap*): the tap is the page's own path
   (`takeSecond` with `how` TAPPED); a spoken *nothing else* would lean on the fake classifier reading the second ask's
   escape, which this repository has not held.
7. **The persona question and the first option are matched by shape** (regex), since they name the WHO and the idea:
   no word list per trade, no hard-coded actor.
8. **The 130 words were re-pinned beyond `interviews_screens.py`** (`vectors_screens.py`'s persona and L1 words, the two
   L1 holds, the back-test's describers): FR-4 asks for every 130 word the harness reads on the five screens.

## What did not hold

- **IM2 and the L1 *no price* assertion meet keel-web 130 / 132's L1 sub.** 130 FR-2 puts *... which uses Keel's
  credits* on L1 and 132 FR-1 makes it *uses 400 credits*; `interviewer_marks.PRICE_WORD` finds *credits*, so
  `interviewer_leg`'s *L1 revisited ... no price on it* and IM2 on `screens.L1` will fault on the stack. A mark's reading
  is FR-5's *nothing else moves* (and 132 is not this spec's input), so neither was moved: for the coordinator (a spec
  that lets L1 name the recording's price, as 132 decided).
- **Nothing here was walked on a stack.** Every screen change is held by unit doubles and source order; `make eval
  K=s005` / `s006` / `s007` / `s012` are the coordinator's after the merge.
- **`quality/decisions.toml` D-2026-10-30-01** is left for the coordinator to mark `merged` with the merge sha.
