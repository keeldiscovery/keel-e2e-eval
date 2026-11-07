# Tasks 144 -- The walk waits for the review and shoots the Check after the band

Branch `144-the-walk-waits-for-the-review`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-144`
(`.git` a file), cut at master `24d107e`. Against keel-cloud-docs master **`9e4b7fda`** (233 merged; contract 63;
`CARDS_SHA256` `98b7379b...`), read only; keel-web 180 read off its branch `180-save-holds-for-the-review` (worktree
`wt/keel-web-180`, **`c0952419`**) while it was built, then off keel-web master `fbfe96a2` once merged; read only. Nothing paid: no stack, no model, no key, no walk -- the unit
suite only. Not merged; master untouched. The corpus yaml, `quality/decisions.toml`, the readers' prompts and rubric and
`RUBRIC_VERSION` (5) untouched.
keel-web 180 merged during the build: **keel-web master `fbfe96a2`** (the coordinator's word, 2026-11-06) -- the pins read
it there now.

| Commit | What |
|---|---|
| `a187883` | FR-4 the mirrors: the cards' byte copy and digest, contract 63 |
| `b457814` | FR-1 the walk waits (the hold, the second shot, Continue, `review_holds`) |
| `ed627f3` | FR-2 Compatibility's changed rows |
| `6da158b` | FR-3 the record |
| `a4a7a72` | FR-1 pinned to keel-web 180 as built; the page's own 90 s cap read as the same defect |
| `d56d52e` | FR-1 / FR-2 pinned to keel-web 180 as merged (`fbfe96a2`): the walk's ceiling 120 s, Continue sends no PUT, Choose after the review |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-4 the mirrors** (`a187883`).
  - `quality/readers/dimensions.md` copied byte for byte from keel-cloud-docs `9e4b7fda`
    `src/main/resources/keel/dimension-cards.md` (Compatibility §2 only: the review may change a condition that breaks
    the card, the permission example, the founder's words behind Put back, *a settled row is put aside, not noted*).
    sha256 **before `2f4f0bf810dc9a5eb75e5af7986fa1a60ba1937e88af8a1923905e95149618f7`, after
    `98b7379b8fe68d9ef3c393045804b7837ae759c28e061ed8c812bbb2500b1c7b`** (= `RespondentReview.CARDS_SHA256`).
  - The digest pin moved in place, as 142 and 143 moved it: `CARDS_SHA256_141` in
    `tests/test_cloud_219_228_mirror_141.py` (the one constant the 213, 216 and 232 pins read). 143's own pin
    (`test_the_reader_digest_is_232s_cards`) now holds the copy at `CARDS_SHA256_141` and 232's digest as one it may
    have been; its `behind **Put back**` count reads `>= 2` (233 says it twice more on Compatibility).
    `tests/test_cloud_233_mirror_144.py` pins `CARDS_SHA256_233` and the Compatibility §2 words (`behind **Put back**`
    four times, *The settled note:* gone).
  - **Contract pin 62 -> 63** (no harness pin named 62 before; the pins are new): the openapi's `x-keel-contract: 63`
    == `vectors_screens.REVIEW_CONTRACT`; `VectorDtos.AnsweredRows(long revision, List<BeliefRowDto> rows, ReviewDto
    review)` and `ReviewDto(String interactionId)`; the openapi's `review` (`required: [interactionId]`, uuid);
    `pickedIndex`'s description (Compatibility's Check carries none; a pick on a put-aside row 422);
    **`SavedListDto` unchanged since 232** (`..., Integer lineAfter, List<PutAsideDto> putAside, ChangedDto changed)`,
    the 141 pin's signature stands). `vectors_screens.review_of_answer(body)` reads the Save answer's
    `review.interactionId`.
- [x] **FR-1 the walk waits** (`b457814`, `a4a7a72`).
  - `vectors_screens.Corridor.list_check` saves Importance, Current solution and Compatibility (`REVIEWED_LISTS`)
    through `_save_holding`; every other list as before (`_press_primary`). Step by step (the unit test,
    `tests/test_walk_waits_for_the_review_144.py`, on a routed page drawn as 180 draws it):
    1. the Check read and shot as before (`check-{dim}`), the founder's own rows typed where the walk owes them;
    2. Save pressed; the `PUT calibration/{vector}` kept -- its answer's `review.interactionId`, whether its body carried a
       `pickedIndex` (`picked_sent`; 233 FR-2: Compatibility's carries none);
    3. every 250 ms the page read (`_HOLD_JS`): the address, the hold (*Keel is reading your answers* anywhere in the
       drawn text, or `[data-testid=list-reviewing]`), the band (`list-changed`), the primary's words and state;
    4. the address moved -> `moved`: nothing more read (the review changed nothing, failed, or none ran);
    5. the hold seen -> waited until `list-reviewing` leaves. The page caps its hold at 90 s after the Save's answer
       (`REVIEW_HOLD_MS`) and then moves on as if no review ran: a hold that ends by moving on at or past 85 s
       (`REVIEW_HOLD_CAP_S` 90 less `REVIEW_HOLD_GRACE_S` 5) is that cap -> `ReviewHoldStop`: *DEFECT (keel-cloud 233):
       {dim}'s Check held on \*Keel is reading your answers\* {s} s and the page moved on at its own 90 s cap (the Save's
       review: {id}) -- the walk stops here*;
    6. the walk's own ceiling on a hold still drawn is `REVIEW_HOLD_CEILING_S` (120, above the page's, as the coordinator
       set it) -> the page kept as evidence (`Camera.evidence`, `failed-check-{dim}-held`, never a scored screen) and the
       same stop (*... past 120 s ...*). Either way `corpus_scenario._check_screen` files the stop as a finding and in
       `review_holds`, then the stop goes on up;
    7. the Check stays -- the band drawn, the primary enabled and reading *Continue* / *Continue to choose* -> `stayed`:
       the Check read again (`reviewed`: rows as changed with Was and why, the band, the put-aside rows, the *Keel will
       test* box), shot a second time for the reader (`check-{dim}-reviewed`, a founder shot whose record carries
       `review` through `READ_JS`), and Continue pressed (`continue`) -- the PUTs it sent counted (`continue_put`; 180
       FR-2: none on an untouched Check; one sent is a finding). Never Put back (the test counts presses: 0), never an edit
       after the hold;
    8. the writes the press started settle (`SAVE_SETTLE_S`); a 409 is pressed again once (DRIFT #80, as before).
  - `review_hold` per list: `{review, held, held_s, outcome (moved / stayed / timeout), picked_sent, continue_put}` ->
    `Journey.review_holds` -> `backtest.json` `review_holds`; `backtest.md` one line per list (`review_hold_said`).
  - The bundle reads the second shot as its dimension's: `founder_answer` (*read what Keel changed after their Save
    (...), then pressed Continue to choose -- nothing put back, nothing edited*), `read_back` (the dimension's, the box
    as the review left it).
- [x] **FR-2 Compatibility** (`ed627f3`).
  - `corpus_scenario._after_the_review`: after a Compatibility Check whose Save named a review or stayed with the band,
    the calibration is read again and Choose is walked on the saved list as served (`answer.list`: `typed`, `why`,
    `putAside`, `changed`) in place of the draft -- so `_choose_label` picks by label as served, `keel_left_out` /
    `keel_added` (104 FR-1 / 108 FR-2) count a changed row (its `typed`) or a put-aside row present, `_name_keel_added`
    reads the same list. Importance and Current solution have no Choose: their question stands. A Compatibility Check
    Save that sent a `pickedIndex` is a finding (a keel-web before 180), never a stop.
  - `_choose_label`: the golden walk's index shortcut holds only on a list the review left alone (a reviewed list is
    picked by label as served there too). A planned pick the review put aside **falls to the first founder row still on
    the list** (`first_founder_row`: a label they typed, folded, or a row whose `typed` is theirs; Keel's own suggestion
    passed where the mark is Keel's) -- recorded in `Journey.review_picks` (`{planned, why, picked, row}`) ->
    `backtest.json` `review_picks`, `backtest.md`, and a finding; none left stops by name. 143's pin that a put-aside pick
    stopped moved in place to the fall.
  - Choose after the review (`choose_after_review_faults`, keel-web 180 FR-3): the options are the rows as served -- no
    put-aside row among them -- and the Choose Save posts the rows as served (labels) with the pick; each miss a finding,
    never a stop (`choose_faults` holds the pick and its served index as before; the pending box *Pick one and the test
    appears here.* is the existing *nothing pre-picked* check).
  - `review_changed` / `band` per list: `vs.lists_reviewed` was already generic over every saved list; pinned on 233's
    recorded Compatibility list.
  - A changed row over the served cap (Compatibility's 16): `review_defects` files `DEFECT (keel-cloud 233)` on
    Compatibility (232 on the other two), left as served, never a retype, never a stop.
  - The strict stored-list check (`reviewed_as_saved`) holds the pick by its words (the picked row's `typed`, else its
    label), or the row it fell to -- never the index, which the reviewed list moves.
  - The stranger's item: the harness's `spoken.kind_of` reads the rewritten row (no stored kind) as PERMISSION (the
    registry's four) and the founder's words behind Put back as ABILITY; keel-cloud's own pin
    (`TheReviewChangesTheConditionsTest`: *Think of your last booking call. Were you allowed to have unanswered calls
    forwarded to another number?*) read off the checkout.
- [x] **FR-3 the record** (`6da158b`).
  - `quality/cards.fold_reviewed`: `{dim}-reviewed` -> `{dim}`. `readers.founder_screens` reads `check-{dim}-reviewed`
    as kind `check`, dimension `{dim}` (so it is sent `{dim}`'s card and scored on R7); `checked_beliefs` names it
    *{dim}, after Keel's review*. `table.rows` folds a recorded `{dim}-reviewed` into `{dim}`'s row (score files written
    either way); `cycle.failing_screens` (the adviser) matches it under that row.
  - The cycle: each study of a 144 bundle (one that records `review_holds`) carries `review_dims` (per dimension
    `{changed, put_aside}`, the three, zeros kept) and `review_shots` (the `check-*-reviewed` screens); the record's
    review line, with the switch ON, reads *the review (spec 209, keel-cloud 232, 233): N founder rows changed and M put
    aside over K walks (...) -- Importance a changed / b put aside, Current solution ..., Compatibility ...; the Check
    shot again after the band (keel-cloud 233, spec 144) on S screens: {entry · scope} \`check-...-reviewed\`, ...; the
    readers scored the screens as served, the second shots under their dimension*. A record of walks before 144 reads
    as 143 wrote it (pinned).
  - `RUBRIC_VERSION` 5 stands; no file under `quality/readers/` but the vendored cards changed.
- [x] **FR-5 the gate** -- below.

## Gate

`set -o pipefail; make unit 2>&1 | tail -2` against keel-cloud-docs `9e4b7fda`:

- Before (master `24d107e`): the five digest pins are red against `9e4b7fda` (the copy `2f4f0bf8`, the cloud
  `98b7379b`): `test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed`,
  `test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`,
  `test_cloud_216_mirror_139::test_the_cards_are_the_vendored_copy_at_216s_digest`,
  `test_cloud_219_228_mirror_141::test_the_reader_digest_is_the_clouds_vendored_cards`,
  `test_cloud_232_mirror_143::test_the_reader_digest_is_232s_cards` (the run's other four reds were files this builder
  was editing mid-run; each passed alone and in every run after).
- At `6da158b` (FR-1..FR-4): **5676 passed, 81 skipped in 320.42s, 0 failed**.
- At `a4a7a72`: **5678 passed, 81 skipped in 323.12s, 0 failed**.
- At `d56d52e` (the last code; this commit adds tasks.md only): **5679 passed, 81 skipped in 318.75s (0:05:18), 0 failed**
- +28 tests: `tests/test_cloud_233_mirror_144.py` (5, FR-4), `tests/test_walk_waits_for_the_review_144.py` (8, FR-1),
  `tests/test_compatibility_review_144.py` (10, FR-2), `tests/test_record_review_144.py` (5, FR-3). Three pins moved in
  place (`CARDS_SHA256_141`; 143's digest pin and Put back count; 143's put-aside pick -> the fall); none weakened
  beyond the count's `>= 2`.

## Judgement calls

1. **The second shot's slug is `check-{dim}-reviewed`** (the spec writes `…-check-reviewed`): kind first, as every
   founder slug (`_FOUNDER_KIND`), so the readers, the bundle and the table read its dimension by stripping one suffix;
   the file is `founder-NN-check-{dim}-reviewed.png`.
2. **The hold is read by its words first** (`LIST_REVIEWING` in the drawn text, the button's or the status line's), and
   180's `list-reviewing` id beside them; the primary by its existing selector (`.ccard__foot button.btn.primary`,
   which 180's `list-primary` button is). *Stayed* needs the band, the primary enabled and reading *Continue* / *Continue
   to choose*, and the Save's answer seen (or the hold seen).
3. **The spec's 90 s cap is the page's** (keel-web 180 counts it from the Save's answer and moves on as if no review
   ran); the walk reads a move at 85 s or more as that cap -- the `DEFECT (keel-cloud 233)` stop -- and keeps its own
   ceiling of 120 s on a hold still drawn (the coordinator's: *a ceiling above 90 s*). A hold that ends sooner and moves
   on is `moved` (no defect: the review landed and changed nothing, or failed -- 233 FR-1's refusal statuses move on by
   rule).
4. **The interaction is not polled by the walk**: the page polls it (180 FR-1); the walk reads the page and records the
   id the Save named. The walk's own wire reads stay as 143 had them (`lists_reviewed` at the end).
5. **Choose is walked on the re-read saved list only where the review changed it** (a band or a changed / put-aside
   row); otherwise the question as drafted stands, so a walk with the switch off reads exactly as before.
6. **"The first founder row still on the list"** is the first served row whose label the founder typed (folded:
   case, stops, spacing) or whose `typed` is theirs; Keel's suggestion passed only where the mark is Keel's (Adoption
   and Purchase friction; on Compatibility keel-cloud 121's mark is the founder's row, spec 138).
7. **The golden walk picks by label too on a reviewed list** (the index shortcut would land on the wrong row once a row
   is put aside); on a list the review left alone the golden walk is unchanged.
8. **`DEFECT (keel-cloud 233)` on Compatibility, `232` on the other two** -- the spec that changes the rows.
9. **The stored pick is held by its words**, since 233 moves rows (a put-aside row leaves, a put-back row goes to the
   end).
10. **The record's per-dimension line is written only for a 144 bundle** (`review_holds` recorded); a 143 bundle's study
    keeps 143's line byte for byte.
11. **`backtest.py` carries `review_picks` from the FR-1 commit** (one transcript line beside `review_holds`, empty until
    FR-2 fills it).

## Pinned to keel-web 180

Read off **keel-web master `fbfe96a2`** (180 merged; first read off its branch at `c0952419`, worktree `wt/keel-web-180`):
`translate.ts` -- `LIST_REVIEWING = "Keel is reading your answers"`, `LIST_CONTINUE =
"Continue"`, `LIST_CONTINUE_CHOOSE = "Continue to choose"`; `ListQuestion.tsx` -- the hold's status `p.calib__drafting
.calib__reviewing[role=status][data-testid=list-reviewing]` in place of the band, the primary
`button.btn.primary[data-testid=list-primary]` (disabled, reading `LIST_REVIEWING`, while holding), the band
`list-changed`, `aria-busy` while it holds; `KEEL_TEST_PENDING` *Pick one and the test appears here.* (Compatibility's
Choose before the pick); `reviewHold.ts` -- `REVIEW_HOLD_MS = 90_000`. The coordinator's account of the merged hooks
(2026-11-06): the hold `[data-testid=list-reviewing]` (role=status, exactly the words), `list-primary` reading the same,
disabled, `aria-busy="true"`, polling every 2 s, giving up 90 s after the Save's answer; then *Continue* / *Continue to
choose*, enabled, no PUT; 179's hooks unchanged; Compatibility's Choose the served rows as unchecked radios, no put-aside
row; its Save the rows as served plus `pickedIndex` -- each pinned above or held by the walk (findings). `test_the_hold_is_pinned_to_keel_web_180s_words_and_ids`
reads keel-web's checkout first (`stack.toml`), then `keel-web-180` beside it or under `wt/`, and skips by name where
none has 180.

## Owed / open

- keel-web 180 is merged (`fbfe96a2`); its tasks.md's Owed wire was taken from the coordinator's summary and the
  source, not re-read line by line.
- The page's 90 s cap and the walk's reading of it are the same number by design (keel-cloud 233 *Open 1*: no server-side ceiling); a
  sweeper that fails an unclaimed read-back is keel-cloud's own spec.
- No keel-cloud defect filed from this spec: no walk ran. The cycle (paid, the founder's word) runs with
  `KEEL_REVIEW_RESPONDENT_QUESTIONS=true` exported, its *Why* naming it; any `DEFECT (keel-cloud 233)` it meets is in the
  bundle's findings and `review_holds`.
- The readers' text for a second shot is the screen as served (the band, the changed rows, Was, the put-aside rows on
  the screenshot and in `rows` / `review`); no reader prompt names it (RUBRIC_VERSION 5).
