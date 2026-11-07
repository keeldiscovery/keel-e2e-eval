# Tasks 145 -- The harness mirrors keel-cloud spec 235 (the ladder rewritten as one scale)

Branch `145-mirrors-of-spec-235`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-145` (`.git` a file),
cut at master `858ec91`. Against keel-cloud-docs master **`74a04fb5`** (235 merged; contract 63 unchanged; screen
contract 25 unchanged; `CARDS_SHA256` `3041f69c...`), read only. keel-web owed nothing (235's *Owed*). Nothing paid: no
stack, no model, no key, no walk -- the unit suite only. Not merged; master untouched. The corpus yaml,
`quality/decisions.toml`, the readers' prompts and rubric and `RUBRIC_VERSION` (5) untouched.

| Commit | What |
|---|---|
| `019ea4e` | FR-1 the mirrors: the cards' byte copy and digest, the band's new line in the fixtures |
| `2ece4c1` | FR-2 the record: ladders rewritten whole, the longest hold per dimension |
| `7c80e41` | FR-3 the walk on Codyco's ladder rewritten whole (tests only) |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1 the mirrors** (`019ea4e`).
  - `quality/readers/dimensions.md` copied byte for byte from keel-cloud-docs `74a04fb5`
    `src/main/resources/keel/dimension-cards.md` (Current solution §2 *The notes*: the five rewritten as one scale on
    the first rung's measure, never a condition, held whole, one more turn inside the Save's hold, the band's new line;
    Importance §2 *The notes under the rows*: a part, a cause or a means of the own row put aside, never reworded).
    sha256 **before `98b7379b8fe68d9ef3c393045804b7837ae759c28e061ed8c812bbb2500b1c7b`, after
    `3041f69cc95ae3ae951e5fd7a393c89acdc05ff31e9b67f3d48261ee4220ebcc`** (= `RespondentReview.CARDS_SHA256` at
    `74a04fb5`).
  - The digest pin moved in place, as 142/143/144 moved it: `CARDS_SHA256_141` in
    `tests/test_cloud_219_228_mirror_141.py` (the one constant the 211, 213, 216, 232 and 233 pins read). 233's pin
    (`test_the_reader_digest_is_233s_cards`) now holds the copy at `CARDS_SHA256_141` and 233's digest as one it may
    have been. 232's card pin (`test_the_two_amended_sections_say_the_review_may_change_a_row`) reads either heading:
    *The review may change such a rival** (keel-cloud 232)* or *(keel-cloud 232, 235)*; *The review may change such a
    rung** (spec 232)* or *The review rewrites the five as one scale** (specs 232, 235)*.
  - The band's line in the mirror fixtures: `tests/test_cloud_232_mirror_143.py`'s Codyco `CURRENT_SOLUTION` now
    carries 235's first line (*Keel rewrote the scale so every answer is a step in how soon a missed call was called
    back.*, the ladder rewritten whole); `CURRENT_SOLUTION_COUNTED` keeps 232's (*Keel changed three answers so they sit
    on one scale.*, the measure dropped); `review_band` reads each as served, `review_changed` the same rows either way.
  - `tests/test_cloud_235_mirror_145.py` (4): the digest (`CARDS_SHA256_235` == `CARDS_SHA256_141` == the cloud's);
    the two amended sections' words; `ReviewedRows.changed`'s two Current solution lines read off the checkout (the
    fixtures' words are the cloud's); the band read as served by `review_band`, `lists_reviewed` and `backtest.md`
    (235's tasks.md Codyco table: the second answer applied whole, `lineAfter` 1, the three whys).
  - No harness code builds or matches the band's words: the record and the reader read whatever line is served, as
    before. No `instructions/` pin reads the read-back contract (235's optional `measure` is never served).
- [x] **FR-2 the record** (`2ece4c1`).
  - `quality/cycle.study_review(study, record)`: the bundle's review readings, moved out of `walk_one` (143 FR-1/FR-2,
    144 FR-3 as before) and two more, only on a bundle that records `review_holds` (144's walk and later), switch ON:
    `review_scales` -- 1 where Current solution's served band opens *Keel rewrote the scale*
    (`SCALE_REWRITTEN`, read as served, never built), else 0; `review_held` -- `{dimension: {held_s, outcome}}` for the
    three reviewed lists whose Save held (`review_holds`, spec 144 FR-1). `Study` and its data block carry both (absent
    where None, so a record before 145 keeps its shape).
  - `review_line`, beside the per-dimension counts: *N Current solution ladder(s) rewritten whole as one scale (the
    band's \*Keel rewrote the scale ...\*, keel-cloud 235); the longest hold on Save (each bundle's `review_holds`):
    Importance x s (walk), Current solution y s (walk), Compatibility none*; the head cites *keel-cloud 232, 233, 235*. A
    longest hold whose `outcome` is `timeout` is said as *the page's cap: DEFECT (keel-cloud 233), the walk stopped* --
    the stop itself is 144's, untouched (`REVIEW_HOLD_CAP_S` 90, grace 5, ceiling 120, `ReviewHoldStop`, pinned). A
    record of walks before 145 reads as 144 wrote it (pinned).
  - `tests/test_record_review_145.py` (7): three fixture bundles (Codyco: 235's band, Current solution held 41.3 s;
    Fresco: 232's count line, the measure dropped; Palus: an Importance hold of 88.4 s at the cap) walked through
    `walk_one` with a fake runner, composed, rendered and read back. The line as the fixture record prints it:

    ```
      - the review (spec 209, keel-cloud 232, 233, 235): 6 founder rows changed and 1 put aside over 3 walks (each bundle's `lists_reviewed`) -- Importance 0 changed / 1 put aside, Current solution 6 changed / 0 put aside, Compatibility 0 changed / 0 put aside; 1 Current solution ladder rewritten whole as one scale (the band's *Keel rewrote the scale ...*, keel-cloud 235); the longest hold on Save (each bundle's `review_holds`): Importance 88.4 s (10-palus · PROBLEM -- the page's cap: DEFECT (keel-cloud 233), the walk stopped), Current solution 41.3 s (21-codyco · PROBLEM), Compatibility none; the Check shot again after the band (keel-cloud 233, spec 144) on 3 screens: 21-codyco · PROBLEM `check-problem.current_solution_satisfaction-reviewed`, 08-fresco · PROBLEM `check-problem.importance-reviewed`, 08-fresco · PROBLEM `check-problem.current_solution_satisfaction-reviewed`; the readers scored the screens as served, the second shots under their dimension
    ```
- [x] **FR-3 the walk** (`7c80e41`, tests only -- nothing new built, as the spec says).
  - `tests/test_ladder_rewritten_whole_145.py` (5), on Codyco's five as 235 FR-7 / its tasks.md serve them (typed *Some
    called back when there was time* / *Few were ever called back* / *Calls that rang out were simply lost* -> *Called
    back the next day* / *Called back days later* / *Never called back*; rungs 1 and 2 the founder's, untouched): every
    rung present by `typed` (`missing_rows`, `held_by_review`, `founder_words`); the leading rungs served verbatim
    (064 FR-5a); `rungs_plan` plans no edit off the wire (and three without `typed`: the check bites);
    `_rungs_to_type` plans none off the *Was:* lines alone; `reviewed_as_saved` holds the stored ladder as the founder's;
    no cap defect. On a routed Check (`_check_screen` -> `list_check`): Save, a hold of 1.2 s standing for 235's two
    turns waited out, the Check stays with the scale's band and three changed rungs, read and shot again
    (`check-problem.current_solution_satisfaction-reviewed`), Continue pressed; one PUT, no rung typed, **Put back
    pressed 0 times**; `review_held` / `review_scales` read what that walk wrote.
- [x] **FR-4 the gate** -- below.

## Gate

`set -o pipefail; make unit 2>&1 | tail` against keel-cloud-docs `74a04fb5`:

- Before (master `858ec91`): the copy `98b7379b`, the cloud `3041f69c` -- the digest pins red (`make unit` was not run
  whole at `858ec91`; with only the new cards copied, `test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`
  was the first red of the mirror files, the chain of pins that read `CARDS_SHA256_141` with it).
- At `7c80e41` (the last code; this commit adds tasks.md only): **5695 passed, 81 skipped in 331.97s (0:05:31), 0 failed**
  (144 closed at 5679 passed, 81 skipped: +16, nothing else red).
- +16 tests: `tests/test_cloud_235_mirror_145.py` (4, FR-1), `tests/test_record_review_145.py` (7, FR-2),
  `tests/test_ladder_rewritten_whole_145.py` (5, FR-3). Pins moved in place: `CARDS_SHA256_141`; 233's digest pin; 232's
  two card headings (either round's words); 143's Codyco fixture band (235's line) beside a new counted fixture (232's
  line). None weakened.

## Judgement calls

1. **"Rungs 2-5 all changed"** (the brief) is read as 235's tasks.md table: rungs 3-5 changed, rung 2 *All called back
   that day* kept (the brief says so too); the founder's leading rungs untouched is 064 FR-5a's half of the check.
2. **The ladders rewritten whole are counted on Current solution's band alone** (`review_scales`), by its opening words
   as served, never by building the line; 0 or 1 a walk.
3. **The longest hold is per dimension over the walks, named by walk**, from `review_holds`' `held_s` where the Save
   held (a Save that never held is not a hold). The record cannot tell one read-back turn from two (no wire field, as the
   spec wants); the hold's length is where a second turn shows.
4. **The new clause is written only where a study carries 145's fields**; a record composed before keeps 144's line byte
   for byte, and a 144 bundle walked into a 145 record is read with the new fields (it records `review_holds`).
5. **`review_defects` still names keel-cloud 232 on Current solution** (the cap is 232's hold; 235 moves no cap).

## Owed / open

- The cycle (paid, the founder's word): `export KEEL_REVIEW_RESPONDENT_QUESTIONS=true`, BUILD = `74a04fb5`'s short sha,
  *Why* naming spec 235 and comparing against cycle 16 (fits 78.0; Current solution 63.9, Importance 55.0). Its record
  will say the ladders rewritten whole and the longest holds; the model's time on the light tier over two turns is the
  cycle's to record (235 measured 97 ms on the stand-in runtime).
- keel-cloud 235 *Open* 1 and 2 (AirCaps' seat rewording passes code; a half-rewritten ladder with no condition word
  passes code) are keel-cloud's; the readers will see them on the screens as served.
- No keel-cloud defect filed from this spec: no walk ran.
