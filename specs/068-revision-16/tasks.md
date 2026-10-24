# Tasks 068 -- Corpus revision 16 and the walks of keel-web 106's screens

Branch `068-revision-16` off master `876e95d` (worktree `wt/eval-068`). The cloud half is keel-cloud-docs master
`efdd37bf` (spec 129, corpus revision 16, `canon/designs/measured-beliefs/sim/check_corpus_r16.py`, the mirrors
`src/test/resources/keel/corpus-r15/`, `backtest-r15/`, `corpus-r16/`, contract 36 in `canon/openapi-v2.yaml`); the web
half is keel-web master (`3651081`, 106 built, contract 36 vendored: `OCCASION_ON_THE_WIRE = true` in
`src/lib/contextOccasion.ts`), its selectors in `specs/106-after-the-batch-web/tasks.md`. One commit per section below,
in this order, each gated on `.venv/bin/python -m pytest tests -q` and a case-insensitive grep of its output for
`failed` / `error`. No `make backtest`, no live model: the host-door re-runs are the parent's.

Unit suite with `REVISION = 16` alone, before any other change: **226 failed, 2,711 passed, 53 skipped, 191 errors**
(the fixtures at 15 -- 282 of the errors' lines are the fixture refusal --, `test_corpus_r15.py` diffing against r14,
the marks header's digests at r15, and the spoken record read with 128's Commitment options).

## FR-1 -- revision 16 (first: it unblocks every load)

- [x] T001 `instructions/corpus.py`: `REVISION = 16`; `_REVISION_OF[15]` names revision 15 as *before keel-cloud 129*
  (112 back-test Commitment picks `yes_after_trying` on a step-alone list); the module's account gains revision 16.
- [x] T002 fixtures (`tests/fixtures/corpus/09-fixture.yaml`, `10-fixture-b2b.yaml`, `tests/fixtures/backtest/99-broken.yaml`)
  at revision 16; the registry slice (`tests/fixtures/registry/slice.yaml`) unchanged -- 129 moved no registry json or
  yaml (`git diff 423f0983 efdd37bf` names none), named here so the next reader does not look for an edit.
- [x] T003 `instructions/marks.py`'s header: a *Corpus revision 16* paragraph naming the seven golden files by sha256
  (canon bytes at `efdd37bf`, equal to `corpus-r16/`); v20 stands; the two cut Commitment options named as served words.
- [x] T004 the golden mirrors: `spoken.served_labels` writes Commitment's options as 129 does (`ItemFrames.firstYes` /
  `secondYes` / `cutToFit`, FR-15: the step cut by its trailing phrase to its share of nine; FR-9: never *first first*),
  so the record is read back whole -- 03-lullaby's *Yes, I'd allow it to use the microphone* and 02-compliancelog's
  *Yes, after a look at it first* (word changes only).
- [x] T005 `tests/test_corpus_r15.py` becomes `tests/test_corpus_r16.py`: D16 mirrored -- every entry beside the cloud's
  r15 mirrors, every difference the revision line or a step-alone back-test entry's `yes_after_trying` -> `yes_start`,
  the moved picks per entry exactly 129 T028's listing (112, Issen's seven by name), nothing else; the cloud's
  `check_corpus_r16.py` prints OK on all 35; all 35 load at 16 (the 28 in back-test mode) and r15's 11-issen is refused
  by name; 067's rule-Q, answer-box, rung, follow-up, needs-input, spoken-guard, changed-screen and register tests kept.
- [x] T006 the tests that read fifteen read sixteen (`test_corpus_r11_shape`, `test_instruction_corpus_r11`'s refusal
  table gains revision 15, `test_instruction_marks`, `test_instruction_spoken`'s Lullaby Commitment).

Measured: **3,131 passed, 53 skipped, 0 failed, 0 errors**; the grep clean. (The rename of `test_corpus_r15.py` to
`test_corpus_r16.py` rode in the tasks.md commit, content unchanged there; its D16 content is this section's.)

## FR-5 -- contract 36

- [x] T010 wherever this repository reads `ContextFields`: the context Save's PUT (`Corridor._save_context`) records
  the fields the page sent (`sent`) and `occasion` apart (contract 36: present once the founder's field holds one; a
  422 `TEXT_REFUSED` past eight words keeps its body); the confirmed context's GET is read with `fields.occasion` (the
  founder's, else the noun the job derived, absent for none or *time*) into `j.screens["context_wire"]` with every PUT's
  occasion. Nothing in this repository names the contract version as a number to bump (no vendored openapi copy; the
  `contract 33` / `contract 35` comments name where a rule came from, not the wire today), so none moved.
  `tests/test_revision_16_walk.py` (stub page). Unit: 3,132 passed, 53 skipped, 0 failed.

## FR-2 -- the spoken mirror follows the served escapes

- [x] T020 `instructions/spoken.py`: `item_escape(registry, key, entry)` -- the escape an item names is the registry's,
  except Ability to pay on a consumer link, served as the budget item with *I can't say* (Issen's 2026-10-23 run: the
  guard read the registry's *I can't recall one* and called the clean item RED); Commitment's is none (129 FR-9's escape
  open), an escape served on it an S6 fault. S6 reads `item_escape`; Existing sacrifice off the chain still names the
  registry's *I don't know* and says spec 077's *I can't recall* (`served_escape`), as the record does.
- [x] T021 S4 counts Commitment's options whole at nine (`STEP_OPTION_MAX_WORDS` 11 -> 9, 129 FR-15; the eleven-word
  test is now the nine-word one, Code Four's *Yes, I'd run a free pilot with a few officers* a fault). `spoken_form`
  109 of 109 on the golden record (`build/spoken-corpus.txt` at `efdd37bf`). Unit: 3,134 passed, 53 skipped, 0 failed.

## FR-3 -- the moved people's lines

- [x] T030 the reader keeps each revision-16 back-test entry's *Changed:* people (`Entry.commitment_moved`, read off the
  entry's own header -- the 112 across the 28, Issen's seven), refusing a named person who is not in the entry or whose
  Commitment pick is not `yes_start`.
- [x] T031 a moved person's bare line written for the second yes -- the line the r15 walk owed first on Commitment
  (`vs.moved_line_for_the_second_yes`: their picks with Commitment read as r15 served it on a step-alone list, *probably
  not*, on the static ladder) -- takes Commitment's rung (`follow_up_dimension`), so 067 FR-3's machinery types it only
  where the served follow-up is Commitment's, which a `yes_start` is never owed: it is skipped, on any rung, and the walk
  names it (`corpus_scenario._moved_line`: *no follow-up was asked* / *the server asked X*). Six of the 112 are such
  lines (Issen's Farida Haque, Imani Brooks, Tobias Wren; Taiga's Sofia Alvarez; RealRoots' Chloe Dubois; Frizzle's
  Jordan Whitaker); a moved person whose line the r15 walk owed on an earlier rung keeps it there, named when typed
  (judgement call 1).
- [x] T032 129's composer mirrored where the harness composes the owed follow-up (the golden journeys hold the route to
  it; judgement call 2): Current solution's and Relative advantage's text is their spoken line (129 FR-3,
  `SAID_AS_SPOKEN`; S-006 and S-007 met *You said it would not have made much difference. What would have?*), a
  have-fact answered No is said back as the fact (129 FR-6, `vs.had_no`), the would-not-pay text said as it reads, and
  Purchase friction's this-purchase words on the long purchase's second stem too (*What would take the time?*, S-006 /
  S-007). Unit: 3,140 passed, 53 skipped, 0 failed.

## FR-4 -- the walks of keel-web 106's screens

- [x] T040 the reads, on 106's selectors: the occasion field (`Corridor.context_occasion`: `context-occasion`,
  `input#context-occasion`) and, after the confirm, `fields.occasion` beside every PUT's (FR-5); the gate's No as served
  (`noLabel`, *I didn't* where the gate asks a want); the name box and `idea-name-suggestion` (`idea_check`'s
  `suggestion`); the needs-input screen answered once on the page (`Corridor.needs_input`: `context-needs-input`,
  `.cneeds__q`, its box, `context-needs-input-send`; `context-reasked` read; the wire only where the page draws
  neither); the Another-country fields (`MarketStep.other`: `market-other-currency`'s first option, `market-other-line`,
  handed out by `create_project(seen=...)`); the stage pages' and the Insights boxes' bar words (`brief_facts.bar_words`,
  the wire's `choice.optionCounts` read too) with no split note past the bar; the GUESSED words apart
  (`insights-guessed`, `report_marks.guessed_of`; a theme's count unchanged, its quotes the said ones); the Purchase
  friction row at 390 (`Answers.friction_row_at_phone`, `boxes_overlap`); the consumer report's own words
  (`report_marks.consumer_report_words`: tiles, leads, rows, the boxes' heads, headings, frames, theme labels, footers,
  the not-asked lines; never a quote). The plan screen after a closed price stays 067's read (`plan_after_closed_price`).
- [x] T041 the holds: on a golden walk each is asserted where the study carries it (the occasion field drawn with the
  entry's occasion and the confirmed `fields.occasion` the same; no suggestion where the seed names nothing; the gate's
  served No drawn; the bar words; the GUESSED words apart; the friction row on a B2B study; the consumer words on a
  consumer one); on a back-test each is a finding, and `backtest.changed_screens` carries them (`web_106`) into
  `backtest.json` / `backtest.md`. Unit: `tests/test_revision_16_walk.py`.

## From the golden journeys (run on the 129 build, keel-web master with contract 36 vendored)

S-006 and S-007 had not been run since before keel-cloud 125; on the 129 build they failed, one fault after another,
each the harness's reading behind the product (no product fault among them), each fixed where it was met:

- [x] T050 `contacts_fake.PRICE_VERSION` 10 -> 11 (`InferenceCharge.VERSION` since keel-cloud 125; no price moved): CM2.
- [x] T051 the backfill's served follow-up map is keyed by rung alone (118's `#also` clips stored beside the rung,
  read by item id, F-15), and IM27 holds an `#also` clip beside its rung as the leg already did (the record's meaning
  unchanged, `INTERVIEWER_MARKS_VERSION` stays 7).
- [x] T052 the dry run's first ask is the segment chip where the gate serves one (05-paidly: *Do you work mostly for
  agencies?*), read by the page itself (keel-web 096 FR-3), so the founder's classify route is required only where
  the first ask is an item.
- [x] T053 Frequency's card on a stored gate (129 FR-1, T003): *the middle answer · days they {the gate's clause}*
  (`brief_facts.card(clause=...)`, the journey's scripted clause); the corpus's reading (no gate) unchanged. 129 says
  *days* whatever the window's unit (05-paidly's *2 months out of 3* reads *days they waited ...*): mirrored, named
  open below.

Measured: unit **3,149 passed, 53 skipped, 0 failed**; S-006 and S-007 **2 passed** (467 s) on the local stack with the
fake interviewer; S-005 stops before anything this spec touches (below).

## Judgement calls

1. **Which of the 112 lines were written for the second yes.** A bare line names no rung, and the file's words are
   not read for intent. The rung the revision-15 walk owed first is the record: where it was Commitment (their
   `yes_after_trying`, served as *probably not* on a step-alone list, the first answer against), the line answered the
   second yes and is Commitment's now; where an earlier rung was owed, the line was typed there at 15 and revision 16
   does not move it (Commitment is the ladder's last rung). Lines whose words speak of trying first but were owed an
   earlier rung (Karsa's Rubina Gill, Palus's Felix Brandt, ...) are typed where they were, named by the walk.
2. **129's composer is mirrored in this build.** Not in FR-1 to FR-5, but the golden journeys hold the follow-up's text
   and spoken line to the harness's own composition (`_hold_the_follow_up`, strict), and 129 moved them (FR-3) -- left
   alone, S-006 and S-007 fail on the 129 build, as they did when first run here.

3. **106's screens are held where a golden study carries them.** A golden walk asserts what 106 must draw for that
   study (the friction row only on a B2B study, the consumer words only on a consumer one, the Another-country fields
   on no golden study -- all seven are US); a back-test records each as a finding, never a stop.
4. **The journey fixes ride in FR-4's commit.** They are not FR-4's rules, but acceptance 1 is the golden journeys
   green, and each was the harness reading the product behind its build (T050-T053).

## Left open

- **S-005 (01-countly) is red, before any leg this spec moved**: keel-cloud 128 FR-14's L16 refuses the golden
  Compatibility condition *Staff could scan the delivery as it arrived* as the idea's own job (Countly's mechanism
  *scans each delivery on arrival ...*), the applier asks a repair turn, and keel-runtime 0.8.0's scripted executor has
  no screen for CALIBRATION_QUESTIONS' context with `repair` (*cannot infer a screen from context keys [..., repair,
  ...]*), so SOLUTION's calibration job fails. A golden entry the cloud's own rule refuses is the cloud's or the
  corpus's to settle (never the corpus here); the runtime's repair key set is keel-runtime's. Not fixed here.
- 129's Frequency line says *days* on a month window (05-paidly): the cloud's wording, mirrored.
- The host-door re-runs (acceptance 3 of 129) and the register rows: the parent's.

## Acceptance

1. Unit suite green; the golden seven's numbers and marks unchanged on the 129 build (v20 stands); S-005, S-006, S-007
   green on the local stack with the fake interviewer.
2. Every revision-16 entry loads (a unit test loads all 35, the 28 in back-test mode).
3. No queued chain whose command line carries the words `pytest evals`.
