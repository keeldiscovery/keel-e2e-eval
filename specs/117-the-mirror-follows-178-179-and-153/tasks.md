# Tasks 117 -- The harness's mirrors follow keel-cloud 178/179 and keel-web 152/153/154

Branch `117-the-mirror-follows-178-179-and-153` (worktree `wt/keel-e2e-eval-117`, `.git` a file, its own `make venv`),
off master `88772e4` (`c3e46c7` + this spec; 4,755 passed / 0 failed / 0 errors / 53 skipped against keel-cloud-docs
`2f147fe7` and keel-web `7243de7`). Built by Claude on 2026-10-31. Read only: keel-cloud-docs master `2f147fe7` (178's
and 179's tasks.md, *The keel-e2e-eval pins*; `BriefFacts.java`, `Compare.java`, `SavedList`), keel-web master `7243de7`
(152's, 153's and 154's tasks.md, *What keel-e2e-eval must read*; `translate.ts`, `KeelTest.tsx`, `ListQuestion.tsx`,
`founderLists.commitmentHolds`, `FounderControl.tsx`, `spokenAnswers.chipSaid`). **No stack, no model, no walk, no
Gradle, no npm, no paid call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `cae0942` | FR-1: `instructions/brief_facts.py` in 179's tense; three tests re-pinned; the DRY reader's tolerance (`retense_179`) |
| `a159d6c` | FR-1 / FR-2 / FR-3: the page objects (`harness/vectors_screens.py`, `harness/vectors_script.py`) |
| `190acd4` | FR-1 / FR-3: `corpus_scenario.said_faults` and its `leg_calibrate` step |
| `afe9a5a` | FR-4: the story sheet's two chips, the tap by words, the refusal said (`interviewer_screens`, `interviewer_fake`, `interviewer_leg`) |
| `1741f70` | FR-4: the after-answers leg by keel-web 154's ids (`evals/backtest.py`); 109's FakePage re-pinned |
| `57cc5eb` | FR-5: `tests/test_mirror_follows_117.py` (43) |
| the docs commit | this file and `AGENTS.md`'s spec-117 paragraph |

## Unit (the gate)

| | passed | failed | errors | skipped |
|---|---|---|---|---|
| master `88772e4` (as handed over), keel-cloud-docs `2f147fe7`, keel-web `7243de7` | 4,755 | 0 | 0 | 53 |
| **branch at `57cc5eb` (the last code; the docs commit adds none), the same siblings** | **4,799** | **0** | **0** | **53** |

+44 tests: 43 in `tests/test_mirror_follows_117.py`, 1 in `tests/test_instruction_brief_facts.py` (the tolerance's own
pin). The 53 skipped are master's 53. `make unit` was run from the worktree (05:52-05:56 ET).

## FR-1 keel-cloud 179 -- `cae0942`, `a159d6c`, `190acd4`

- [x] T001 `instructions/brief_facts.py`: `KEEL_BAR[PURCHASE_FRICTION_KEY]` *holds if at least 2 in 3 say it would be
  needed and would take a long time*; `friction_words` held *Yes, {step} would slow it. Plan for it.*, not held *Your
  fear was {step}. k of n said it would be quick or not needed. Not the blocker you expected.* (docstring too); the card
  line *would need {step}, and it would take a long time*. Read against `BriefFacts.java:177/909/960-962`.
- [x] T002 Re-pinned with why: `test_instruction_brief_facts.py::test_purchase_friction_counts_the_fear_held` (line,
  bar named in full, both words, and none of *last time / took / was quick / was needed / slows it*);
  `test_after_131.py` `FEAR` (S-014's 130-build words re-worded as 179 serves them; the test holds the pill to the card's
  served word, whatever its tense); `test_report_marks.py::test_the_lead_lines_follow_the_stage_status`.
- [x] T003 **Compare's status line / insight / drift clause**: no mirror exists in this repo (searched `harness/`,
  `evals/`, `instructions/`, `quality/` for *took a long time*, *was quick*, *plan for it*, *not the blocker*, *a split:*,
  *can slow or stop*) -- 179's tasks.md found none either. Nothing to move; the walk reads them as served.
- [x] T004 **`tests/fixtures/sample/s006-reads.json` NOT edited.** It is a recorded read of 05-paidly from before
  keel-cloud 118 and 179 (*... said it was quick or not needed* in Purchase friction's `statusLine` and `driftClause`;
  *did not need ..., or it was quick* on its card). No test held its friction words to a mirror (its readers,
  `test_sample_export.py` and `test_backtest.py`, pass it through), so it already tolerated the tense; a new test
  (`test_the_recorded_s006_read_is_the_old_tense_and_still_exports`) says so: the export of the read as recorded and of
  the same read re-tensed as 179 serves it both pass, and it asserts the recording still says *was quick* so whoever
  re-records it is told to drop the tolerance. **Owed: re-record it** (`make sample`, the coordinator's).
- [x] T005 **Compatibility's Choose title** (179 FR-1, `SavedList.COMPATIBILITY_CHOOSE_PROMPT`): the walk reads
  `seen["prompt"]` (`.listcheck__title`; keel-web draws the served prompt over its own) and now holds it to *Which one do
  you want to test?* (`vs_screens.CHOOSE_PROMPT`), in `said_faults` (T010).

## FR-2 keel-cloud 178 -- `a159d6c`

- [x] T006 No reader of the answers view's word existed (178's tasks.md searched too). `vs.ANSWERS_VIEW_NOTHING` =
  `VALUE_BOX_LABELS["NOTHING"]` = *None* (`CommercialChain.NOTHING_LABEL`, the answers view's `interview.items[].answer`
  and the Pilot tab's `answers[].words`), for any check that reads it. The note at `harness/vectors_script.py:983`
  (*The labels were Nothing and I don't know until keel-cloud 170*) stays; a test holds both.

## FR-3 keel-web 153 -- `a159d6c`, `190acd4`

- [x] T007 **The mirrors** (`vectors_screens`): `IMPORTANCE_ANSWER_HINT`; `COMPATIBILITY_ANSWER_HINT` (a pattern: *at
  {segment}* or none, the segment the context's -- not held to a word, it is the page's lower-casing of the founder's);
  `CHOOSE_PROMPT` (Buyer and payer 116's, Purchase friction and Compatibility *Which one do you want to test?*; Adoption
  friction unmoved and not held); `PURCHASE_FRICTION_CHOOSE_INTRO`; `PURCHASE_FRICTION_CHOOSE_BAR`; `COMMITMENT_BAR` /
  `COMMITMENT_DECIDER_BAR` and `commitment_bar` (cases `decider`, `same`; the deciders are 149's `deciderPlural` of the
  persona, recorded and not held to a word, as 116 holds Buyer and payer's; *of them* is a decider case);
  `COMPATIBILITY_KEPT_NOTE` (`keeltest-note`); `FREQUENCY_RANGE_HINT` (`frequency-range-hint`); `IMPORTANCE_COUNT_FREE`
  and `importance_count_free`.
- [x] T008 **What the page objects read.** `list_answer` unchanged (`seen["hint"]` is the first `.calib__hint`, as 153
  says). `list_choose` adds `intro` (`.corridor__intro`) and the box's last line before and after the pick
  (`note_before`, `note`); `_keel_test` is unchanged (153 J-4: the note is outside `.keeltest__t` / `.keeltest__b`).
  `single` adds `range_hint` on a `numeric_interval` screen, read as it opens.
- [x] T009 **Importance's count-free box**: the walk reads the Check box after `.calib__drafting` detaches and once the
  list holds the own item and more, so 153 changes nothing it asserts (`_hold_importance_check` unchanged); a count-free
  box read there is given back whole by `importance_count` and named by the hold. Pinned.
- [x] T010 **One step holds them** (`leg_calibrate`, after 116's): *each screen says what it tests -- the Answer hints,
  the Choose titles, Purchase friction's intro and bar, Compatibility's kept line, Commitment's bar, Frequency's range
  hint (keel-web 153, keel-cloud 179; spec 117)* -- `said_faults(screen, key, b2b=j.entry.b2b())`, every fault
  `{dimension, what, drawn, want}`, on the golden and the live walk alike. Unsure list dimensions are skipped (as 116's).

## FR-4 keel-web 152 and 154 -- `afe9a5a`, `1741f70`

- [x] T011 **Two chips.** `Player.sheet()` adds `chips` (every `.iv-chips .chip`, served order); `chip` stays the first
  (*I can't recall one particular {occasion}*), so IM22's `_chip_ends_it` and `tap_chip()` are unchanged (its walked
  entries now record `chips` too). `_Walk.story` taps a scripted `anchorChip` other than `CANT_RECALL` by its words
  (`tap_chip_named(fake.story_chip_word(...))`: *I'd rather not say*) -- it tapped the first chip whatever was scripted.
- [x] T012 **The refusal said.** `interviewer_fake.story_chip_said` mirrors 152's `chipSaid` (`escapeSaid`'s fold plus
  `AROUND_A_CHIP`, `stripCommands`, the words half of `norm`). The walk speaks each scripted story; one that IS the
  refusal would end the interview with no story and no items, which that person's expected body does not say, so
  `_Walk.story` stops by name there (script it as the chip). No golden (71 stories) or back-test (375) story is one --
  a test holds it.
- [x] T013 **The after-answers leg by 154's ids.** `STAGE_JS`: the root `stage-page` (else `.corridor.answers`; its
  `data-stage` recorded as `stage`), the verdict `stage-verdict` (else `p.answers__headline`), the rows
  `stage-dimension` (else `.dimrow`) keyed by `data-dim` (else `id`), `opens` from `data-opens` (else a
  `button.dimrow__head` inside), each row's status `dimension-verdict` (else `span.status`). `CARD_JS`: the card by
  `data-dim`, the drawing `dimension-chart` (else `.dimrow__drawing`; the kind still read inside it), the verdict
  `dimension-verdict`, the count `dimension-count` (else `span.status .sub`). Both record `by_ids`. `STAGE_ROW` and
  `card_selector` are CSS selector lists, the id first; the head `CARD_OPEN` = `stage-dimension-open` /
  `button.dimrow__head`; the body `.dimrow__body` (no id). A test reads a 154-shaped page and a classes-only page in
  Chromium and gets the same record.

## FR-5 -- `57cc5eb`

- [x] T014 `tests/test_mirror_follows_117.py` (43), each moved mirror pinned with why; the re-pins above (T002, and
  `test_after_answers_109.py`'s FakePage reading the selector list).

## Where the spec and the code differ (the code's patterns followed)

- **The DRY compare against a stale build.** `make unit` reads keel-cloud's `build/brief-facts/` beside the checkout,
  and the one there was written at 01:36 ET, before 179 merged: with the mirror moved, the two DRY tests (101 checks,
  49 checks) met exactly three Purchase friction cards (05-paidly, 06-repeatline, 07-mulchrun) differing in `line`,
  `keelBar` and `statusWords` by 179's tense, nothing else. The code's pattern for a build older than a moved line is a
  skip (`_at_145`, `_at_159`), which would have dropped the whole compare. Instead `cloud_facts_at_104` moves a pre-179
  build's Purchase friction cards by 179's own table (`TENSE_179`, the three strings alone) so every other word is
  still held to the byte; a no-op on a 179 build. Remove it once the build is rewritten.
- **"Make its test tolerate the tense" (s006)**: no test held the recording's friction words, so nothing needed
  loosening; the tolerance is stated and pinned by a new test (T004) rather than by editing a reader.
- **Compatibility's prompt is held where the walk reads it** (`said_faults`), beside Buyer and payer's (`choose_faults`,
  116), not by changing `choose_faults`.
- **Faults, not a hard stop per screen**, as 114 / 116.

## What still needs re-recording (owed, the coordinator's)

1. `tests/fixtures/sample/s006-reads.json` (`make sample`): the old tense; the new test then drops its *was quick*
   assertion.
2. keel-cloud's `build/brief-facts/` (a `BriefFactsCorpusTest` run): pre-179 at this build; the DRY compare tolerates
   it (above), and the instruction eval's `brief_facts` mark on cycle 4 should read a fresh one.
3. The gallery fixtures (`tests/fixtures/gallery/*-08-fresco/*`) and `quality/scores/*` quote the old words: records of
   their cycles, never rewritten.

## What the spec did not foresee

1. **The walk tapped the first story chip whatever was scripted** (T011): harmless while the AI sheet drew one chip; with
   152 a scripted `rather_not_say` would have sent `CANT_RECALL`.
2. **The screen of record on Frequency** (`evals/backtest.py`'s `hint: one(".calib__hint, ...")`) now reads the range
   hint, the first `.calib__hint` on that screen (153 says so); it is the hint the founder sees, so it stays.
3. **No live check of the new step**: the acceptance (a golden walk on the local stack, or a back-test) is the
   coordinator's. On a keel-cloud before 179 or a keel-web before 153 the new step fails by name -- intended.
4. **154's body has no id**, so `.dimrow__body` is still read by class (154's table names none).
