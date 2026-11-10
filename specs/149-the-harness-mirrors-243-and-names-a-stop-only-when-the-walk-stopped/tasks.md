# Tasks 149 -- The harness mirrors keel-cloud 243 and keel-web 184, and names a stop only when the walk stopped

Branch `149-the-harness-mirrors-243-and-184`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-149` (`.git`
a file, asserted first), cut at master `a3bbfce`. Built by a builder (Claude Opus 5.5) on 2026-11-09 ET. Read only:
keel-cloud-docs master **`c87d1066`** (243 merged: `specs/243-*/tasks.md` *Owed: keel-e2e-eval 149* and *The staging
shape*, `dimension-cards.md`, `RespondentReview.java`, `ReviewedRows.java`, `SavedList.java`,
`TheReadBackIndexIsNeverMisappliedTest`, `canon/openapi-v2.yaml` at `x-keel-contract` 64) and keel-web master
**`82a746d9`** (184 merged: `specs/184-*/tasks.md` *Owed: keel-e2e-eval 149*, `KeelChanged.tsx`, `ListQuestion.tsx`,
`translate.ts`). Also read (read only, never written): cycle 19's two bundles and their walk logs in the main checkout's
`runs/`. Nothing paid: no stack, no model, no key, no walk, no journey, no cycle -- the unit suite only. Not merged;
master untouched; every commit pushed as it landed. The corpus yaml, `quality/decisions.toml`, the readers' prompts and
rubric and `RUBRIC_VERSION` untouched; the committed cycle 19 record not rewritten.

**Contracts**: `x-keel-contract` **63 -> 64** (`vectors_screens.REVIEW_CONTRACT`; 144's pin reads `>= 63`);
`ScreenResponseContracts.CONTRACT_VERSION` **25 unchanged** (pinned).
**Digest**: `CARDS_SHA256` **before `78bd11674018b1e2644b2de99256e1fe3c2c781e0f6fca7cefab68fe98e86307`** (241, the step
before), **after `94fd69c097176c877571e300312eb2d380788fbcc0a9358fe31d1881b86b6be5`** (243) = `RespondentReview.CARDS_SHA256`
at `c87d1066`.

| Commit | What |
|---|---|
| `32670c2` | FR-1 the cards' byte copy, the digest chain moved, contract 64 |
| `9baf10c` | FR-2 the read-back mirror: numbered rows, the shift, a row in place of each put aside, the band counts both |
| `5a3c606` | FR-3 the walk reads the Check as 184 draws it; Choose's pick and the record carry the pair (and FR-4's hold) |
| `6ad4213` | FR-4 the staging shape pinned: the mirror test and the scripted Importance journey's assertion |
| `2e64920` | FR-5 stopped early only where the walk did not reach its end; the stop named |
| `119dfba` | FR-6 the record's review line cites 243 and counts *suggested in place* |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1 the digest and the contract** (`32670c2`). `quality/readers/dimensions.md` copied byte for byte from
  `c87d1066`'s `dimension-cards.md` (243: Importance §2 -- *Keel adds none but a row in place of one the review puts
  aside*, **In place of each row put aside, Keel suggests one**, the rows numbered from 0, the Check's pattern, the
  band; Relative advantage §2 and Compatibility §2 likewise). `CARDS_SHA256_141` moved in place (`78bd1167...` ->
  `94fd69c0...`); 148's digest pin holds 241's as one it may have been (as 147 did 237's). `REVIEW_CONTRACT` 63 -> 64.
  `tests/test_cloud_243_web_184_mirror_149.py` pins `CARDS_SHA256_243`, 241's as the step before, the card words, and
  the contract (64, the four fields named; screen contract 25).
- [x] **FR-2 the read-back mirror** (`9baf10c`). `harness/vectors_script.py`, a new section mirroring 243 FR-1 to FR-4:
  `numbered` / `labels_of` / `read_back_context` (Importance's rows, Current solution's rungs, Relative advantage's
  benefits and the ladder beside them, `[{index, label}]` from 0; Compatibility's conditions were 236's); `review_shift`
  (`shiftOf`) and `read_back_answer` (readings, `shift` = the log's `review.shift`, the refusal line *index 7 is outside
  the 4 rows handed (0 to 3)*, 236's top-level `suggest`); `read_back_notes` (`readBackNotes`, shifted);
  `in_place_applied` (each `drop` put aside with its own note; a `suggest` beside it standing where the dropped row
  stood -- `suggested`, `suggestedWhy`, `inPlaceOf`; `replacedBy` on the put-aside; a suggestion beside no drop, blank,
  with no why or saying a row again refused; the floor counting only the bare drops, the last first; a `label` applied as
  the row changed); `band_line` (`ReviewedRows.changed`'s lines) and **`band_counts`** (`BAND_CHANGED`,
  `BAND_PUT_ASIDE`, `BAND_IN_PLACE`: the served line's three counts -- *the band regex counts both*). Existing helpers:
  `review_changed` records `replacedBy` (served, else read off the rows) / `keels` / `typedKeels` where served (absent
  otherwise, so a list before 243 reads as 143 wrote it); `review_in_place` and `lists_reviewed[dim].in_place` name Keel's
  rows with the row each stands for; `review_suggested` carries `inPlaceOf`; `founder_words` / `as_drafted` leave Keel's
  row in place out (the row put aside is the founder's -- else the strict `reviewed_as_saved` would count one row twice).
  `tests/test_read_back_rows_149.py` (19 with the band parametrisation), checked against the cloud fixture's own strings
  where the checkout is there.
- [x] **FR-3 the walk** (`5a3c606`). `harness/vectors_screens.py`: 184's hooks as constants; `keel_row` (kind, `n`, the
  line's lead, the words behind it -- `was` on a reworded row as 179's *Was:* was read, `in_place_of` on a row in place --
  the why from `row-why`, whether Put back is drawn) and `keel_record` (each entry's kind, whose, `n`, struck words, tag,
  reason, what stands now, its own Put back); `record_put_aside` turns the record's *replaced* / *aside* entries into the
  rows put aside (`replaced_by`, `keels`). `_list_rows` reads them (the textarea is read as a descendant, so the box inside
  `span.listrow__box` is found); 179's hooks are still read on a web before 184; nothing is ever pressed. The over-cap cut
  skips Keel's rows the review wrote. `evals/backtest.py` `READ_JS` (the readers' screen) reads the same:
  `review.in_place`, `review.record`, the reworded rows' words off their line, `put_aside` with `replaced_by`, Keel's
  standalone suggestion among `suggested`; `reviewed_did` no longer says *Was*; `backtest.md` names Keel's row in each
  place. `evals/corpus_scenario.py`: `check_pattern_faults` (the Check as drawn against the list as served: each Keel row
  in place drawn *In place of* its row with Put back, each reworded row *Reworded from* its typed words with Put back, a
  suggestion with none, no row drawn with *Was*, numbers shared with the record, each put-aside in the record -- *Replaced
  by* its Keel row, or its own Put back -- and its owner); on Choose, where the planned pick was put aside and no founder
  row is left, the pick falls to Keel's row in its place first, else the first suggested row (147's rule, several now);
  `review_picks` records `replacedBy` / `inPlaceOf`; the suggestion finding names the row each stands for (*keel-cloud 243
  FR-3*). `tests/keel_pattern_184.py` writes 184's DOM from a served list (`keelKindOf` / `keelChanges` mirrored);
  `tests/test_check_pattern_184_149.py` (7).
- [x] **FR-4 the regression shape** (`5a3c606` the code, `6ad4213` the tests). `vs.in_place_faults(handed, saved,
  first_fixed, notes)`: the right rows struck (every put-aside a row the founder saved, never the own row), each reason
  on its own row (present, no two alike, and none more about another saved row than its own -- `reason_row`, content
  words shared), a Keel row in each place (standing where the struck row stood, `inPlaceOf` its words; none standing for a
  row not struck), nothing lost, the band counting both; and a note kept under a row is about that row. The scripted
  Importance journey: **S-005** (01-countly, the corridor, `corpus_scenario.run`) and **S-015** (its problem study,
  `scope_journey.walk`) walk Importance's Check through `leg_calibrate` -> `_after_the_review` -> **`_hold_in_place`**,
  which on a Check that stayed with the band asserts both (`in_place_faults`, `check_pattern_faults`) in a named step on
  the strict walk, and files each fault as a finding (never a stop) on the back-test. `tests/test_staging_shape_149.py`
  (6): the named mirror test (own + 3, the 1-based answer with three distinct reasons, `review.shift` 1, the three struck,
  a Keel row in each place, the band); the misread (the same answer read from 0 -- the staging bug) named *a reason on the
  wrong row* and *a note on the wrong row*; each rule alone; the strict step passing on 243's shape and failing by name on
  the misread; the back-test's findings.
- [x] **FR-5 stops** (`2e64920`). `evals/backtest.py`: `reached_end` (passed, or the last lap one of `END_LEGS`: the
  report leg, the scoped report, the export), `walk_stop` (`{kind: rule | product | harness, step, after, said}` -- a
  retried refusal is never a stop), `stop_of_bundle` (a bundle before 149, read off its laps, step and retried refusals
  against `RETRIES`), `stop_said`; `Backtest.finish` writes `reached_end` and `stop` from the exception that ended the walk
  (`corpus_scenario.run` now keeps it as `ended_by`, so a stop raised outside any step is named); `backtest.md` says
  where and why. `quality/cycle.py`: `Study.reached_end` / `stop` (`study_stop`), `walks_of` counts *stopped early* only
  where the walk did not reach its end, `_stop_step` says the stop by its kind and leg, the per-study table too; a
  record before 149 reads as it was written (pinned). **Cycle 19 re-read** (`tests/test_stops_149.py`, 7, on
  `tests/fixtures/cycle19/` -- the fields the record reads copied verbatim from the two bundles' `backtest.json`, each
  source's sha256 kept): **13 of 15 reached their end**; the two named *after leg_interpret_problem -- a product stop: 3
  refusals of Keel's AI retried (the walk's 3 retries spent), the last at failed-problem-calibration-RESULT_INVALID; the
  refusal past them is in the walk's log*; the gate line **5** E7 / E9 refusals over 15 walks, no walk stopped by rule.
  See judgement call 1: not the spec's *15 of 15*.
- [x] **FR-6 the record** (`119dfba`). `cycle.review_in_place` / `Study.review_in_place` (set only on a bundle of 149's
  walk, the one that records `reached_end`); on such a record the review line cites `IN_PLACE_CITED` (*spec 209,
  keel-cloud 232, 233, 235, 236, 237, 238, 239, 240, 241, 243*), the head reads *n founder rows changed, m put aside and k
  suggested in place (keel-cloud 243) over w walks*, each dimension *c changed / a put aside / k suggested in place*. A
  record of 148's walks reads as 148 wrote it (pinned). `tests/test_record_review_149.py` (3).
- [x] **FR-7 tests** -- below.

## Gate

`make unit` (the worktree's `.venv` a symlink to the main checkout's venv, ignored by git) against keel-cloud-docs
`c87d1066`, keel-web `82a746d9`:

- Before (`a3bbfce`): **10 failed, 5773 passed, 81 skipped in 337.48s** -- the nine digest pins (211, 213, 216, 219-228,
  232, 233, 235, 237, 241) and 144's `test_the_contract_is_63` (243 moved it to 64).
- After (`119dfba`, the last code; this commit adds tasks.md only): **5829 passed, 81 skipped in 316.08s (0:05:16), 0 failed**, 2026-11-09 20:08 ET -- the ten back to green, nothing else red; +46 tests (5783 -> 5829).
- New pins, named for what they guard: `test_cloud_243_web_184_mirror_149` (the digest, the cards, contract 64),
  `test_read_back_rows_149` (the numbering, the shift, the pairs, the floor, the band's counts, the record's words),
  `test_check_pattern_184_149` (184's Check read, the pattern held, Choose's pair), `test_staging_shape_149` (the staging
  shape and its misread, the strict step), `test_stops_149` (the stop rule, cycle 19 re-read), `test_record_review_149`
  (the review line). Moved in place, none weakened but the contract pin (`== 63` -> `>= 63`, 64 pinned in the new file):
  `CARDS_SHA256_141`; 148's digest pin.

## Judgement calls

1. **FR-5's premise does not hold, and the pin says what the bundles say.** The spec reads cycle 19's two *no step
   named* stops as walks that *reached their end and were scored*, with `gate_refusals` all `stopped: false`. The bundles
   (and the walks' logs) say otherwise: both walks' last lap is `leg_interpret_problem`, their founder screens end at the
   problem card (no calibration, lock, invite or export), three refusals were retried each (08-fresco three E9; 17-expanse
   two E9 and one E2), the walk's three retries were then spent, and a fourth refusal -- **E2, the event over eight words**
   (*'found photos or notes missing from the daily log' is 9 words*; *'had a job fail on a wrong resource request' is 9
   words*) -- ended the walk, raised by `_wait_calibration` outside any step, so no step was named and, E2 not being a
   gate rule, no `gate_refusals` entry was marked `stopped`. They were scored on the screens served before the stop. So
   the rule is built as FR-5 states it (*stopped early* only where the walk did not reach its end; a retried refusal never
   a stop, counted on the gate line alone) and the re-read pins **13 of 15**, both stops named (*after
   leg_interpret_problem -- a product stop*), 5 refusals on the gate line -- never *no step named*. Pinning *15 of 15*
   would have pinned a walk that never reached the calibration as complete. For the founder / coordinator: the stop is a
   keel-cloud finding (E2 refusing the AI's event four times running on two studies), not a harness one.
2. **The fake runtime's read-back is a mirror, not a scripted answer.** Nothing in this repo answers a review read-back
   (147 judgement call 11; the strict journeys run with the switch off, the cycle on Keel's model). FR-2 is built as the
   cloud's reading mirrored (`read_back_context`, `read_back_answer`, `in_place_applied`, `band_line`), which the walk's
   assertion and the record's counts use; code's word rules for a suggestion (`spokenFault`, `rowFault`, `pieceFault`)
   are not mirrored -- the mirror holds the places, the reasons and the counts.
3. **The scripted Importance journey's assertion is structural** (`in_place_faults`): the review's raw answer is not on
   the wire (`InteractionView` carries no result), so the walk holds the list as served against the rows saved -- the
   struck rows, the pairs and their places, the band -- and a reason's row by the content words it shares (`reason_row`:
   at least two shared, no other row as near). That catches the staging misread (each reason lands on the row above);
   a reason that names no row's words is not judged. There is no DRY mode for a journey: the assertion runs offline in
   `test_staging_shape_149` against the mirror's wire, through `_after_the_review` itself.
4. **`_after_the_review` now reads the calibration again on a non-picked list** (Importance, Current solution, Relative
   advantage) where the Check stayed with the band -- only with the review ON (one GET; a journey stub without `get` is
   left alone).
5. **Choose's fallback prefers the pair** (several suggested rows now): Keel's row in place of the planned pick, else the
   first suggested row (147's rule).
6. **The 184 reader keeps 179's**: a web before 184 is read as before (no fault for the old drawing on such a page;
   `check_pattern_faults` holds only a page that draws Keel's rows or the record). A changed row drawn without Keel's
   line on a page that draws the pattern is a fault (*Was*).
7. **`reached_end` marks a bundle of 149's walk** (always written by `finish`); `review_in_place` is set only on such a
   bundle, so a record of earlier walks keeps its line byte for byte.
8. **The cycle 19 fixtures are trimmed copies** (the fields the record reads, verbatim; `said` / `why` cut to 240
   characters; each source file's sha256 in `_source`): the bundles live in the main checkout's git-ignored `runs/`.
9. **FR-4's code landed in FR-3's commit** (`_hold_in_place` uses both checks); FR-4's commit is its named tests.
10. **Commit trailers** name the model that built them (*Claude Opus 5.5*, the session's attribution), not the brief's
    *Claude Fable 5.1* -- 147's and 148's precedent.

## What the next cycle will show (paid, the founder's word)

- Where the review puts rows aside: Keel's rows in place on the Check (*In place of "..."*, numbered to *What Keel
  changed*), read and shot as served; `backtest.json` `lists_reviewed[dim].in_place` and `review_changed[].replacedBy`
  (`keels` / `typedKeels` where Keel's words); `review_picks` with `replacedBy` / `inPlaceOf` where a Compatibility pick
  fell to Keel's row; findings *Keel's review suggested at the Check: 'X' in place of 'Y' -- why (keel-cloud 243 FR-3)*.
- New findings, never a stop on the back-test: *{Dimension}: a reason on the wrong row (keel-cloud 243)*, *... a note on
  the wrong row*, *... no Keel row stands in place of a row put aside*, *... Keel's row does not stand where the row put
  aside stood*, *... the band does not count the list*, and the page's (*keel-web 184*): *Keel's row in place is not drawn
  *In place of* its row with Put back*, *a changed row drawn with *Was* (keel-web 179)*, *a row put aside is not in the
  record*, and the like.
- The record: the review line cites *keel-cloud ... 241, 243* and counts *k suggested in place* in all and per
  dimension; a walk that did not reach its end is named *after {leg} -- a {rule | product | harness} stop: {the words}*
  (never *no step named*); a refusal retried is counted on the gate line alone.
- `backtest.md`: *stopped after leg_interpret_problem -- a product stop: PROBLEM's calibration questions FAILED: ...*
  where cycle 19 said *stopped at: --*.

## Open

1. **Cycle 19's two PROBLEM walks stopped on E2 past the retries** (judgement call 1): a keel-cloud question (the event
   over eight words, four refusals running), not filed from here -- no walk ran.
2. The spec's FR-5 sentence (*15 of 15 reached their end*) wants the coordinator's correction to *13 of 15, the two
   stops named*.
3. 243's *Open 1* (the instruction unscreened) and 184's *Open 1* (not walked live) stand: only a paid cycle with the
   switch ON shows the pairs served.

## Read

- keel-cloud-docs `c87d1066`: `specs/243-every-read-back-names-its-rows-and-suggests-in-place/tasks.md`,
  `dimension-cards.md`, `RespondentReview.java` (`numbered`, `labelsOf`, `readBackReadings`, `readBackNotes`, `shiftOf`),
  `ReviewedRows.java` (`rows`, `held`, `floor`, `standing`, `positionOf`, `changed`), `SavedList.replacedBy`,
  `TheReadBackIndexIsNeverMisappliedTest`, `canon/openapi-v2.yaml` (`x-keel-contract` 64, `InteractionView`),
  `ScreenResponseContracts.CONTRACT_VERSION`.
- keel-web `82a746d9`: `specs/184-one-pattern-for-every-row-keel-changed/tasks.md`, `KeelChanged.tsx`,
  `ListQuestion.tsx` (`EditRow`, `CheckList`), `translate.ts` (the pattern's strings).
- This repo: specs 147, 148, 149; cycle 19's record; the two bundles
  `runs/20261109T194118Z-backtest-08-fresco`, `runs/20261109T211406Z-backtest-17-expanse` and their walk logs
  `runs/quality-walk/20261109T194106Z-20261109-76c633d/{08-fresco,17-expanse}-PROBLEM.backtest.log` (main checkout).
