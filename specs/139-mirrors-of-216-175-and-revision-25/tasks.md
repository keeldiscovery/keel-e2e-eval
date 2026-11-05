# Tasks 139 -- Mirrors of 216 and 175, and revision 25

Branch `spec-139`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-139` (`.git` a file). Nothing paid;
no stack, no model, no key; the unit suite only. Against keel-cloud-docs master `04d95c2b` (216, 217 and 218 merged) and
keel-web master `a73c4f5c` (175 merged); neither checkout edited. Not merged; master untouched. No reader, rubric or
`MARKS_VERSION` moved (`quality/readers/dimensions.md` is the cards' byte-equal copy).

| Commit | What |
|---|---|
| `5e61266` | FR-1: the cards at 216's digest; the 137 pin reads it |
| `51e5dc4` | FR-4: revision 25 -- `GALLERY_REVISION`, the loader's three r25 rules, the walk's *Nothing else*, `test_harness_reads_r25_139`, the re-pins |
| `84ac0f1` | FR-2: 216's mirrors -- the frame, E9, L37b, K12, the paying unit, the scripted no-sayers, the lock notes, `test_cloud_216_mirror_139`, the re-pins |
| `a012bb0` | FR-3, FR-4b: the walk on 175, READ_JS, the So line's rule, `test_web_175_mirror_139` |

- [x] T001 FR-1 the cards at 216's digest: `quality/readers/dimensions.md` = keel-cloud's vendored copy, `2f1a63cc...`;
  the 137 pin (`test_cloud_213_mirror_137`) reads 216's digest beside 213's and 214's.
- [x] T002 FR-2 216's mirrors:
  - the Frequency frame (`wording.window_first` / `frequency_respondent`, `vectors_script.window_first` /
    `frequency_served` / `frequency_held`): *On how many of {window} did you {event}?*, *... did that happen?*; 174's
    opening kept by spec number for stored items (`frequency_respondent_before216`, `frequency_served_before216`,
    `frequency_held_before216`); the cap 9 / 8 unchanged and, like E4 and `fitted`, measured on 174's frame
    (`event_max_words`, `framed_fault`, `e4_fault`: *the Frequency question, as the cap measures it,*), so a clause at
    the cap is served in 19 words;
  - E9 (`wording.no_sayer_fault`, `NO_SAYER_TEST`), L37b (`writers_rules.verb_roots` / `head_verb` /
    `own_row_hurt_fault`, `ING_NOUNS`), K12 (`vectors_script.assurance_fault`, `RISK`, `NEGATED`); E9 read in
    `score.act_that_hurts` (the instruction eval's Prevalence); E9 widened and L37b, K12 added in `backtest.LOCK_NOTES`;
  - the paying unit (`chain.paying_unit` / `organisation`, `AT_ORG`, `ORG_QUALIFIER`, `NO_ORG`; `cost_belief(paying=)`:
    money and a share lost on B2B the paying unit's, 213's decider plural where none is named, hours unchanged); the
    loader reads the recorded sentence by 216's rule (`corpus.spec216_payer`, `VectorCorpusFixture.spec216Payer`);
  - the scripted writer: Prevalence carries `no_sayer` (`vs.NO_SAYERS` for the golden seven, Lullaby's the cloud's
    `VectorFixtures.NO_SAYER`; `NO_SAYER_ANY` elsewhere), Lullaby's `went_wrong` the cloud's *did not know why the baby
    cried*; every scripted and recorded condition passes K12; the v9 fixture's Prevalence carries a no-sayer;
  - the instruction files (founder-lists, respondent-questions, asked, respondent-review) have no byte mirror here (the
    instruction eval reads the cloud's at run time, 137 call 11): a test holds that they say what the mirrors hold;
  - `tests/test_cloud_216_mirror_139.py` (48 with FR-4b's), on the cloud's own `TheWriterNamesTheHurtTest` cases.
  - Re-pins by spec number: `test_seven_templates_115`, `test_cloud_212_mirror_136`, `test_dimension_cards_131` (the
    card's good example; the scripted reader's unit read in the window phrase), `test_controls_089`, `test_after_131`,
    `test_referee_follows_193_123`, `test_instruction_window_frame`, `test_lock_frontier_110`.
- [x] T003 FR-3 175's walk: `vectors_screens.LEAVE_OUT_CHIP = UNSURE_CHIP` (*I'm not sure*, 063's
  `LEAVE_OUT_CHIP_063` the fallback on an older web), `LEAVE_OUT_LINE` read beside it; `answer-own-row` read on the
  Answer (`seen["own_row"]`); the Check rows carry `nobody_else` (`check-nobody-else`) and `suggested` / `why`
  (`li.listrow--suggested`, `check-suggestion`); `BUYER_PAYER_BAR_B2B` and `buyer_payer_bar`'s `b2b`; the fact,
  ability and permission bars (`compatibility_bar_faults`); `free_drawn_faults` (`chain-shape-FREE`,
  `chain-free-hint` read before the price pick). `corpus_scenario`: `choose_faults(b2b=)`, `said_faults` (the chip's
  line, the chip pressed, the own row's tag, *Nobody else* first on Buyer and payer's Check, Compatibility's bar),
  `_hold_the_free_pill`. `backtest.READ_JS`: `leave_out_line`, `nobody_else`, `suggested`, `own_row` (the own row out of
  `rows`, in `text`). `tests/test_web_175_mirror_139.py` (18, three on a page drawn as 175 draws it); re-pin
  `test_reworded_founder_screens_116` (the bar's `b2b`, `choose_faults`' call).
- [x] T004 FR-4 revision 25 (keel-cloud 217, `4369a636`): `GALLERY_REVISION = 25`; a gallery file at 24 refused by
  `_GALLERY_R24`, any other file at 25 by `_NOT_GALLERY_R25`; `gallery_names.toml`'s note. The loader's three rules
  revision 25 needed (calls 1-3 below). The walk sends a one-code Importance pick with `chip: NOTHING_ELSE`.
  `tests/test_harness_reads_r24_135.py` -> `tests/test_harness_reads_r25_139.py` (16): the diff 24 -> 25 the gallery's
  alone against `backtest-r24/`, AirCaps' `read_and_watch` index 1 of 2 an ability, the drop shapes (Code Four's and
  Codyco's Purchase friction 2 and 1, the founder's times kept), revision 25's typed-on-Check rows (nine entries).
  Re-pins by spec number: `test_lock_frontier_110` (the three cost questions), `test_money_cards_redrawn_118` (Palus'
  price belief, the r25 fact set), `test_cloud_199_mirror_130` (Expanse's base), `test_adoption_steps_112` (Fresco's and
  Codyco's reworded efforts), `test_cloud_214_mirror_137` (Palus' *cash review* holds X14), `test_gallery`,
  `test_cycle_5_to_the_end_119`, `test_backtest` / `test_instruction_corpus_r11` (calls 1, 2).
  The revision-24 row words of 217's owed list grepped entry by entry outside `quality/` and `runs/`: no live pin or
  harness rule quotes one any more; what remains is docstrings and tests pinned to fixtures, records or synthetic
  cases. The 27 re-read picks and the standings they move (Voltair PEOPLE_DISAGREE, Codyco n 7, Karsa 3 of 7 / 6 of 13,
  AirCaps' Compatibility) are read from the yaml; no eval pin counts them.
- [x] T004b FR-4b (keel-cloud 218): no eval pin quotes Compatibility's So line; the rule (*Whether* + the belief
  lower-cased, its stop dropped) is pinned on 218's three examples off revision 25's beliefs, and no harness, eval,
  instruction or test file says *Whether could*.
- [x] T005 FR-5 the gate: `set -o pipefail; make unit 2>&1 | tail -1` on `a012bb0` against keel-cloud-docs `04d95c2b`
  and keel-web `a73c4f5c`, 2026-11-04 21:42 ET: **5507 passed, 86 skipped in 263.56s (0:04:23)** (0 failed).
  Master `6e42044` on the same siblings is red: 154 failed, 28 errors at the first run (that run overlapped this
  branch's first two edits, so it is not a clean count of master); with FR-1 and the revision line alone, 83 failed and
  26 errors.

## Judgement calls (each with the spec line it bends)

1. **A one-code Importance pick is a whole answer** (FR-4, *the loader reads the fourteen at 25*): revision 25 records
   seven AirCaps Importance answers as one code (217 judgement call 1, *the first pick, then Nothing else*); the loader's
   rule A read *two distinct codes*, so it now reads one or two, and the walk sends the one id with `chip:
   NOTHING_ELSE` (keel-cloud 158 FR-2's wire). The refusal says *one or two*; three is now the refused case.
2. **The occasion is one to five words** (FR-4): Codyco's *shift with a missed call* is five (217: *five words keep
   every framed asked at 20 or under*); rule W read one to four. The cap follows the corpus, not the product's eight
   (`ContextFields.OCCASION_MAX_WORDS`); the broken fixture and the r11 refusal case move to six words.
3. **A re-read Commitment pick leaves revision 16's list** (FR-4, *the 27 re-read picks*): 217 moved Karsa's Sana Memon
   and Mehwish Tariq from `yes_start` to `probably_not`; the revision-16 header still names them under *Changed:*.
   `_commitment_moved` leaves out a person a later revision's head names as re-read on Commitment (*Sana Memon
   (Commitment)*) -- read off the head's words, never by entry.
4. **Codyco's cost question is the port's** (FR-4, *the cost questions the walk now sees*): 217 names three (Palus,
   AirCaps, Expanse, pinned as it says them); Codyco's reworded loss line *Booking calls that rang out unanswered* has no
   verb `LossLine.read` takes (a past), so the port asks *Last month, about what percent of the reservation calls did
   you go without in booking calls that rang out unanswered?* (19 words) -- pinned as composed; the cloud pins none.
5. **E9's missing no-sayer is a fault in the instruction eval's score** (FR-2, *read by name in the lock notes and
   writers_rules / wording where the harness scripts or faults a draft*), as E7's missing `routine` already is; the
   cloud breaches it (refused once, then noted).
6. **The scripted no-sayers are data, not a rule** (FR-2, *the fakes follow the cloud's files*; the house rule, *no
   special cases per entry*): the golden seven's are written in each entry's words beside `ACT_THAT_HURTS` (the
   existing per-entry table), every back-test entry gets the one persona-free `NO_SAYER_ANY`; all pass E9 by test.
7. **L37b on the corpus's own rows is a finding** (FR-2; 137's call 9): the scripted writer drafts the corpus's
   recorded own row, read against the scripted `went_wrong` (the golden seven's own; a back-test entry's *had a time
   when {circumstance}*, revision 25 records no hurt) -- sixteen entries break it, pinned as `L37B_FINDINGS` for a
   corpus revision that records `went_wrong`. Lullaby passes on 216's `went_wrong`.
8. **The B2B bar's form follows the study's B2B flag** (FR-3, *where `b2b`*): `choose_faults` reads `vs.is_b2b(entry)`
   for keel-web's `CalibrationView.b2b` (175 judgement call 1); on that link *Nobody else* carries no *Decided alone
   counts as support.* (175 judgement call 2).
9. **Compatibility's bar is held by its words, not its kind** (FR-3, *a fact row's bar*): keel-web's `isFact` is 128's
   modal test (175 *Left open*), not the cloud's head-verb read, so the walk holds the drawn bar to one of the three
   kinds' words and never 128's *say partly, or no.*, not to the kind the cloud would give.
10. **The own row is read apart from the rows** (FR-3, *read into the screen text the reader gets*): `READ_JS` keeps it
    out of `rows` (an Answer screen draws no Check rows) and gives it as `own_row`; it is in `text` as drawn.

## Left open

- **keel-web 174 retired `COST_PAYER_B2B`** (`lib/costLine.ts`: the persona's BUYER label on B2B); the harness's
  `cost_line_parts` / `cost_line_owed` still says *the buyer's organisation* (137 call 7 read an older web). No unit pin
  reads it; a strict walk's `_hold_the_mode_first` would fault on a B2B entry. Not in 139's FRs.
- Codyco's cost question (call 4) reads poorly; the cloud's ladder serves it as composed. A corpus or cloud call.
- Sixteen L37b findings (call 7) wait on a corpus revision that records `routine` / `went_wrong`.
- Commits carry the brief's `Claude Fable 5.1` trailer; the builder was Claude Opus 5.5.
