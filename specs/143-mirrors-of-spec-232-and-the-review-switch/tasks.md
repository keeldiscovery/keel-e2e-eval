# Tasks 143 -- The harness mirrors keel-cloud spec 232, and the cycle runs with the review on

Branch `143-mirrors-of-spec-232-and-the-review-switch`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-143`
(`.git` a file), cut at master `1a62617`. Against keel-cloud-docs master **`ac81bf6f`** (232 merged; contract 62;
`CARDS_SHA256` `2f4f0bf8...`), read only; keel-web master `ed646e8d` (179 merged), read only, for the Check's hooks. Nothing paid:
no stack, no model, no key, no walk -- the unit suite only. Not merged; master untouched. The corpus yaml,
`quality/decisions.toml`, the readers' rubric and `RUBRIC_VERSION` untouched.

| Commit | What |
|---|---|
| `70780d8` | FR-4 the mirrors: the cards' byte copy and digest, `think_of`, the contract-62 DTO pin |
| `c47788a` | FR-1 the switch in the cycle |
| `0103b77` | FR-2 the walk leaves a changed row alone; FR-3 nothing to build |
| `6bf47d1`, (this) | tasks.md: the gate, the judgement calls, what is open |

## What was built, per FR

- [x] **FR-4 the mirrors** (`70780d8`).
  - `quality/readers/dimensions.md` copied byte for byte from keel-cloud-docs `ac81bf6f`
    `src/main/resources/keel/dimension-cards.md` (Importance §2 and Current solution §2: the review may change a row
    that breaks the card, the Check says so in one line, the founder's words behind Put back; *The rows are never
    rewritten* / *Never a rewrite* cut). sha256 **before `06fcd867112e8fc285e9361061895018fe4739597f33f638bb97481e25f74a53`,
    after `2f4f0bf810dc9a5eb75e5af7986fa1a60ba1937e88af8a1923905e95149618f7`** (= `RespondentReview.CARDS_SHA256`).
  - The digest pin moved in place, as spec 142 moved it: `CARDS_SHA256_141` in `tests/test_cloud_219_228_mirror_141.py`
    (the one constant the 213 and 216 pins read for the current copy). No other digest constant moved (`06fcd867` is
    left only in spec 142's tasks.md and this file, history).
  - The read-back result shape: no `instructions/` (or any harness) pin quotes `readBackContract` /
    `readBackRowsContract` or their `{index, note}` result, so none gained `label` / `drop` (grep of `instructions`,
    `tests`, `harness`, `evals`, `quality/*.py`).
  - The one pin of the wire shape that 232 moved: `test_cloud_219_228_mirror_141::test_the_line_is_read_from_line_or_line_after`
    read `SavedListDto`'s record ending on `Integer lineAfter)`; it now reads 232's `..., Integer lineAfter,
    List<PutAsideDto> putAside, ChangedDto changed)`.
  - The Palus anchor (232 FR-7): `instructions/wording.think_of(whose, occasion)` mirrors `ItemFrames.thinkOf`
    (`LAST_OPENINGS` *your last* / *the last* / *their last* / *last*, in the cloud's order; *Think of the last {rest}.*
    where the occasion opens on one, else *Think of {whose} last {occasion}.*). The harness writes no Importance or
    Current solution anchor of its own (grep: no *Think of your last {occasion}* builder, no pin expecting *last last*);
    it writes ScaleFour's two (`instructions/spoken.at_stake`, `hard_case`), which 232 routed through `thinkOf`, so
    they go through `think_of` now. Pins: `TheAnchorSaysLastOnceTest.theOpenings`'s cases (and *their last*), the
    openings read off `ItemFrames.java`, ScaleFour's two call sites, both anchors on *last 3 months* and *daily log*.
- [x] **FR-1 the switch in the cycle** (`c47788a`).
  - `stack/cloud.review_switch(env)`: `KEEL_REVIEW_RESPONDENT_QUESTIONS` read as Spring reads `${...:false}` into
    `keel.review.respondent-questions` -- `true` / `on` / `yes` / `1` (any case, trimmed) **ON**; unset, empty, `false` /
    `off` / `no` / `0` **OFF**; anything else a `ValueError` naming the variable. `build_env` is untouched: it still copies
    the shell's environment whole and sets nothing (unset in, unset out -- pinned).
  - The bundle: `backtest.json` records `review_switch` (`ON` / `OFF`); `backtest.md` says *review **ON** (spec 209)*
    beside the stack.
  - The cycle: `make quality-walk` reads it at the kick-off (DRY=1 prints *review ON / OFF
    (KEEL_REVIEW_RESPONDENT_QUESTIONS, spec 209)*; preflight refuses a value keel-cloud cannot read, before anything
    runs); each `Study` carries its bundle's `review_switch`; `compose` takes the kick-off's and `review_of` refuses a
    **mixed cycle** (two values among the kick-off and the walks) naming each walk's -- in `walk` the record is then not
    written (exit 2; the bundles and score files stay); `load_record` refuses a mixed record too, so `quality-accept`,
    `quality-advise` and `read-table CYCLE=` refuse a hand-stitched one. The data block carries `review_switch`; the
    head line names it after the reader.
  - Docs: `quality/CYCLE.md` step 1 (`export KEEL_REVIEW_RESPONDENT_QUESTIONS=true` first in the kick-off block, and a
    bullet), README (a paragraph under the readers' section), the Makefile's `quality-walk` comment.
- [x] **FR-2 the walk leaves a changed row alone** (`0103b77`).
  - `harness/vectors_script.py`, generic over every list (no dimension named): `typed_is`, `row_present`,
    `missing_rows`, `held_by_review` (a row present when an item's `label` or `typed` is the founder's words, or a
    put-aside row's `typed` is -- `_same_words`), `typed_by_label`, `put_aside_of` (`putAside` as the wire spells it,
    `put_aside` read too), `review_changed` (`[{typed, label, why}]`, put-aside rows `label: None`), `review_band`
    (`{line, why}`), `changed_over_cap`, `founder_words`, `lists_reviewed`.
  - The strict checks: **104 FR-1 / 108 FR-2** -- `corpus_scenario._choose_label` picks a row whose `typed` is the
    founder's pick by its label as served (a finding *picked as served*, never DRIFT); a picked row put aside stops by
    name as a keel-cloud defect; `keel_left_out` counts a changed or put-aside row present; `keel_added` never calls a
    changed row Keel's. **064 FR-5a / 067 FR-2** -- `vectors_script.rungs_plan` takes `typed` (`{served label: typed}`)
    and never plans an edit over a rung the review changed; `_rungs_to_type` reads it off the wire
    (`served_lists`: the question's `draft` and saved `answer.list`) and off the Check's *Was:* line. **Importance's
    typed rows** (`importance_typed`) -- `_check_screen` drops the rows the review holds (`_not_held_by_review`: a
    finding names them, *never retyped*). The stored-list check -- in strict mode a list the review changed is compared
    read back to the founder's words (`reviewed_as_saved`); in every mode a changed row over the served word cap is
    filed as a `DEFECT (keel-cloud 232)` finding (`review_defects`), never a retype, never a stop.
  - The Check as keel-web 179 built it (master `ed646e8d`, its tasks.md's owed list): `vectors_screens.LIST_ROW` leaves
    out the put-aside rows (`li.listrow--aside`); `Corridor._list_rows` reads a row carrying `row-changed` as
    `changed: True` with `was` (`row-was` `.listrow__was-said`) and `why` (`row-why`, read apart -- the row's `warn` no
    longer picks it up), the band (`list-changed`: `.calib__changed-line` / `-why`) into `band: {line, why}` and the
    put-aside rows (`put-aside` > `put-aside-row`: `s`, `[role=note]`) into `put_aside: [{typed, why}]`.
    `_cut_over_cap_rows` never cuts a row carrying `row-changed` (179 draws it no word count anyway). The camera
    (`backtest.READ_JS`): `rows` and `row_notes` leave out `.listrow--aside`; a shot of a Check the review changed
    carries `review` (`{band, changed: [{row, was, why}], put_aside: [{typed, why}]}`, through `founder_screens` into
    `backtest.json`); a Choose option's changed why (`choose-{dim}-changed-{i}`) is read as the choice's `changed`.
    Nothing in the walk presses Put back (`row-put-back`, `put-aside-back`; pinned over the three walk modules).
  - The bundle: `backtest.json` `lists_reviewed` -- per list the review changed, `{review_changed, band}`, read off
    `GET calibration/{vector}` at the end of the walk (absent where it changed none); `backtest.md` one line per list.
    The record: each study's `review_rows` (`{changed, put_aside}`) and, with the switch ON, one head line *the review
    (spec 209, keel-cloud 232): N founder rows changed and M put aside over K walks*.
  - The Choose pick by label as served: no list 232 reviews has a Choose screen (Importance and Current solution are not
    in `vs.PICKED`), so the rule holds through `_choose_label` for any list a later review changes.
- [x] **FR-3 the reader -- nothing built.** The readers score the screens as served; `RUBRIC_VERSION` stands (5); no card
  of the reader's digest written. Where it would change if it did: `quality/readers.founder_screens` (the founder-reader's
  text of a Check: a line naming `lists_reviewed`'s changes under the rows), `evals/backtest.READ_JS` (the camera's read
  of the band, the *Was:* lines and the put-aside rows into the shot), and `quality/readers.py`'s respondent screens
  read `served` as keel-cloud serves it (the changed rows already).
- [x] **FR-5 the gate** -- below.

## Gate

`set -o pipefail; make unit 2>&1 | tail -1` against keel-cloud-docs `ac81bf6f`:

- Before (master `1a62617`): **5 failed, 5598 passed, 81 skipped in 321.99s** --
  `test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed`,
  `test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`,
  `test_cloud_216_mirror_139::test_the_cards_are_the_vendored_copy_at_216s_digest`,
  `test_cloud_219_228_mirror_141::test_the_reader_digest_is_the_clouds_vendored_cards` (the digest),
  `test_cloud_219_228_mirror_141::test_the_line_is_read_from_line_or_line_after` (contract 62's `SavedListDto`).
- After (`0103b77`, the last code; the commits after it touch tasks.md only): **5651 passed, 81 skipped in 301.77s
  (0:05:01), 0 failed** -- the five back to green, nothing else red. +48 tests: `tests/test_review_switch_143.py` (22,
  FR-1), `tests/test_cloud_232_mirror_143.py` (26: FR-4 13 with `think_of`'s nine cases, FR-2 13). Two pins moved in
  place (`CARDS_SHA256_141`, the `SavedListDto` signature); none weakened.
- One run between (FR-2 before the keel-web 179 hooks and judgement call 9): 2 failed, 5647 passed --
  `test_spec_138_compat_suggested::test_palus_shape_on_adoption_friction_still_stops` (fixed, call 9) and
  `test_vectors_screens_guide::test_the_corridor_frame_counts_the_sheet` (passed alone and in the run after: a flake,
  untouched code).

## Judgement calls

1. **The digest pin moved in place** (`CARDS_SHA256_141`), as 142 did, rather than a new constant: the 213 and 216
   pins read it for the current copy; `test_cloud_232_mirror_143` pins `CARDS_SHA256_232` beside it, equal.
2. **Spring's boolean words** are the switch's (`true/on/yes/1`, `false/off/no/0`); an empty value is read as unset
   (OFF); anything else is refused before the walk (keel-cloud would not boot on it).
3. **A mixed cycle is refused when the record is composed** (after the paid walks: the walks themselves are never
   stopped -- 082 FR-3's rule for a moved sha) and again whenever a record is read. A bundle before 143 (no
   `review_switch`) is never counted as either value.
4. **The record's head line** says *review ON (spec 209)* / *review OFF (spec 209)* after the reader and before the bar;
   a record without the field renders as before (the 079 fixture record is byte for byte unchanged).
5. **The wire's `putAside`**: the spec writes `list.put_aside`, keel-cloud 232 serves camelCase (its judgement call 8);
   both are read.
6. **Present is `_same_words`** (case, spaces and a trailing full stop), the rungs' own reading, for `typed` as for
   `label`.
7. **The README has no cycle section**; the cycle's runbook is `quality/CYCLE.md` (step 1 now opens on the export), and
   the README gained one paragraph under the readers' section.
8. **The walk's decisions read the wire first, the page second**: `rungs_plan` takes the `typed` words off the
   question's lists and then off the Check's `row-was`; the Importance rows, the picks and the stored list read the
   wire alone. The page's hooks (keel-web 179 as built) feed what the shot records and the cap-cut's guard.
9. **`keel_left_out` counts a held row present by the review alone** (`held_by_review`: a `typed` or a put-aside row),
   not by `row_present`'s case-folded label -- that would have read Keel's suggested Adoption friction row as the
   founder's and broken spec 138's pin (`test_palus_shape_on_adoption_friction_still_stops`, red in the first run).

## Owed / open

- **The founder's Check shot is taken before the Save that starts the review**, and the walk moves on after Save
  (Importance and Current solution have no Choose screen). Unless keel-web 179 holds the Check after Save until the
  read-back lands, no founder screenshot shows the band or a changed row; the readers then see what the review did only
  on the respondent's served items. keel-web 179 as built does not hold the Check (its FR-5: the re-read re-opens an
  untouched Check when the founder is on it); a second shot of the Check after the read-back lands (going back to it)
  would be a follow-up here (`_reshot`), on the founder's word.
- No keel-cloud defect to file from this spec: no changed row was seen (no walk ran). The first walk with the switch
  ON (the founder's word) files any `DEFECT (keel-cloud 232)` finding the bundle carries.
- The cycle itself (paid) is out of scope: kicked off after `export KEEL_REVIEW_RESPONDENT_QUESTIONS=true`, its *Why*
  naming it.
