# Tasks 147 -- The harness mirrors keel-cloud 236 and 237 and keel-web 181

Branch `147-mirrors-of-specs-236-and-237`, worktree `/Users/athulrajeev/Documents/projects/wt/keel-e2e-eval-147` (`.git`
a file), cut at master `1585f6e`. Against keel-cloud-docs master **`76620269`** (236 and 237 merged; contract 63
unchanged; screen contract 25 unchanged; `CARDS_SHA256` `42fa94dd...`) and keel-web master **`b8682c4f`** (181 merged;
contract 63, nothing on the wire), both read only. Nothing paid: no stack, no model, no key, no walk, no journey -- the
unit suite only. Not merged; master untouched. The corpus yaml, `quality/decisions.toml`, the readers' prompts and rubric
and `RUBRIC_VERSION` (5) untouched.

| Commit | What |
|---|---|
| `a492f60` | FR-1 the mirrors: the cards' byte copy and digest, the hint, the job in the tail (frame `"237"`) |
| `3df5859` | FR-2 the walk on Relative advantage: the fourth hold, the served belief, the stem on name and frame |
| `e6cca87` | FR-3 the walk on Compatibility: Keel's rows by their `typed`, the review's suggestion Keel's and a valid pick |
| `96419bf` | FR-4 the record: four dimensions, the fourth screenshot, the hard case changed |
| (this) | tasks.md |

## What was built, per FR

- [x] **FR-1 the mirrors** (`a492f60`).
  - `quality/readers/dimensions.md` copied byte for byte from keel-cloud-docs `76620269`
    `src/main/resources/keel/dimension-cards.md` (236: Compatibility §2 -- every row read, Keel's included; a rewrite
    faces the settled test; two rows about one thing are one; the suggestion moves; the permission stem the passive;
    237: Relative advantage §2 -- the benefits read back, the hard case rewritten, the job in the tail; §5's Lullaby
    line; §6's pitfalls of cycles 15-17). sha256 **before `3041f69cc95ae3ae951e5fd7a393c89acdc05ff31e9b67f3d48261ee4220ebcc`,
    after `42fa94dd18d99c3800e507c2225d4e5244d8654425f3287447389ce56c15c0e1`** (= `RespondentReview.CARDS_SHA256` at
    `76620269`; 236's own `204eef55...` passed through, pinned as `CARDS_SHA256_236`).
  - The digest pin moved in place, as 142-145 moved it: `CARDS_SHA256_141` in `tests/test_cloud_219_228_mirror_141.py`
    (the one constant the 211, 213, 216, 232, 233 and 235 pins read). 235's pin (`test_the_reader_digest_is_235s_cards`)
    now holds the copy at `CARDS_SHA256_141` and 235's digest as one it may have been. Card-word pins moved: 233's
    Compatibility pin reads *were allowed to* (236, after 234) and the heading *(keel-cloud 233, 236, ...)*, its Put back
    count `>= 4` (237 adds Relative advantage's); 131's Relative advantage good example is §5's new line.
  - The hint pin (`harness/vectors_screens.COMPATIBILITY_ANSWER_HINT` / `_WANT`) reads keel-web 181's words: *... e.g.
    "could talk over the noise on site" (true for some of them, not all).*; 168's example kept as
    `COMPATIBILITY_ANSWER_HINT_168`, now a fault (`test_mirror_follows_117`). Pinned off `translate.ts`.
  - `instructions/spoken.py` mirrors `ScaleFour.question` at 237: `HELPED` / `HELPED_END`, `helped_tail(job)` (the job in
    the second person, its trailing clause cut, as `ScaleFour.helpedTail`), `idea_ladder(name, what, tail)` (213's ladder,
    its room read off the tail it is tried with), `advantage_question(name, what, job, at_stake)` (the job's tail first,
    then `DONE_BETTER`; the at-stake anchor keeps `DONE_BETTER`), `advantage_anchor` (hard case -> stem -> at-stake, with
    whether it is the at-stake one); `advantage_stem` composes them. Checked word for word against 237's
    `TheBenefitsReadBackTest.theJobInTheTail` (six items) and `RelativeAdvantageHardCaseTest` (219's five, moved in place
    in `test_cloud_219_228_mirror_141`), and 214's pins (`TheWritersKeepTheCardsRulesTest`), moved in place.
  - `harness/vectors_script.benefit_frame_of`: frame **`"237"`** for `BENEFIT_HELPED` =
    `^Would (?P<idea>.+?) have helped you (?P<job>.+?) better, or not\?$`; frame **`"198"`** for
    `BENEFIT_DONE_BETTER` = `^Would (?P<idea>.+?) have done that better for you, or not\?$` (the at-stake tail, and the
    fallback where no rung fits with the job -- it read None before); `"173"`, `"159"`, `"085"` as before;
    `benefit_split` takes the anchor apart.
  - The fake runtime's read-backs (236's `suggested` / `mechanism` context, 237's `{rows, clause, ladder}` and the
    second instruction file): **nothing to build here** -- the harness scripts no read-back (`vectors_script` /
    `corpus_script` answer no review screen; the cycle runs Keel's own model, the strict journeys the scripted executor
    with the switch off). The stand-in runtime of 236/237 is keel-cloud's own test support.
- [x] **FR-2 the walk on Relative advantage** (`3df5859`).
  - `vectors_screens.REVIEWED_LISTS` gains `solution.relative_advantage` (237 FR-1, keel-web 181 FR-2): its Check's Save
    goes through `_save_holding` as the three (144 FR-1) -- *Keel is reading your answers* waited out, the band, the
    second shot `check-solution.relative_advantage-reviewed`, Continue, never Put back; `review_holds[dim]` as before.
    Pinned on a routed page drawn as 181 draws it (the lead benefit left, three `put-aside-row`s, no `row-changed`, the
    box the served belief).
  - A put-aside benefit counts present by its `typed` -- 143 FR-2's generic rule (`missing_rows`, `held_by_review`,
    `founder_words`, `reviewed_as_saved`), pinned on 237's cluster Check; the band with only the moment changed (no
    `why`) is read as served.
  - The belief after the hold: `corpus_scenario.belief_after_the_hold(j, key)` reads the box on the Check that stayed
    (`reviewed.test.belief`); the strict `/review` row check holds the row's belief to it, the corpus's words a finding
    beside it.
  - The stem check (`_hold_the_idea_name`): `advantage_question_want` holds the question **after** the anchor -- strict:
    the harness's composition around the idea's name, its what and the context's job (`helped_tail`; *done that better*
    where the served anchor is the at-stake one, `spoken.held_anchor`); back-test: the ladder over the tail as served,
    so *Would it ...* is held exactly where the name does not fit beside the job (a finding, never a stop; the name in
    the question passes as before). The anchor's words are never held (the review may rewrite the hard case). The fault
    names the frame (`benefit_frame_of`). `review_defects` names keel-cloud 237 on Relative advantage (none can be
    filed: a benefit is never reworded).
- [x] **FR-3 the walk on Compatibility** (`e6cca87`).
  - `vectors_script.review_suggested(saved, draft)`: a saved row `suggested` with its why that the Answer's draft does
    not carry (236 FR-2; the draft's own suggested row, 121's mark, is not it); `as_drafted(saved)`: every row in the
    words it was saved with (a changed row's `typed`, Keel's or the founder's, then the put-aside rows).
  - `_after_the_review`: Choose walks the saved list where the review changed a row, served a band **or added a
    suggestion** (236 serves no band for a suggestion alone), keeping the Answer's draft (`answer_draft`) and the
    suggestion's label (`review_suggested`).
  - `keel_left_out`: a typed row is present near a row's saved words (a Keel's row the review changed or put aside);
    `keel_added`: every row read by its saved words -- Keel's changed row named as served, Keel's put-aside row by its
    words with *(put aside)*, the review's suggestion apart; `_founders_rows` and `first_founder_row` pass the
    suggestion (Keel's).
  - `_name_keel_added`: a finding *Compatibility: Keel's review suggested at the Check: '...' -- why (keel-cloud 236
    FR-2)* beside *Keel added*, never a stop. The pick stays by label as served (144 FR-2); a planned pick put aside
    with no founder row left falls to the review's suggestion (recorded in `review_picks`, a finding naming it) where it
    stopped before.
  - The served stem of an allowed-to row is the passive (*Could unanswered calls have been forwarded to another
    number?*): the harness composes no Compatibility stem; 144's pin reads 236's moved cloud test.
- [x] **FR-4 the record** (`96419bf`).
  - `backtest.json` records `reviewed_lists` (`backtest.reviewed_lists()`, the four).
  - `quality/cycle`: on a bundle that records them, `review_dims` / `review_held` count Relative advantage
    (`REVIEWED_DIMENSIONS_147`), `review_moments` is 1 where its band's `changed.line` says *changed the moment the
    question asks about* (`MOMENT_CHANGED`, read as served). The review line (switch ON) cites *keel-cloud 232, 233, 235,
    236, 237*, says *Relative advantage a changed / b put aside (the hard case changed on m walks: ...)*, its longest
    hold, and *(Relative advantage's, the fourth, on n)* in the second-shot clause. A record before 147 reads as 145
    wrote it (pinned). The line as the fixture record prints it:

    ```
      - the review (spec 209, keel-cloud 232, 233, 235, 236, 237): 3 founder rows changed and 3 put aside over 2 walks (each bundle's `lists_reviewed`) -- Importance 0 changed / 0 put aside, Current solution 3 changed / 0 put aside, Compatibility 0 changed / 0 put aside, Relative advantage 0 changed / 3 put aside (the hard case changed on 2 walks: the band's *... changed the moment the question asks about ...*, keel-cloud 237); 1 Current solution ladder rewritten whole as one scale (the band's *Keel rewrote the scale ...*, keel-cloud 235); the longest hold on Save (each bundle's `review_holds`): Importance none, Current solution 30.1 s (21-codyco · SOLUTION), Compatibility none, Relative advantage 18.4 s (17-expanse · SOLUTION); the Check shot again after the band (keel-cloud 233, spec 144) on 3 screens (Relative advantage's, the fourth, on 2): 17-expanse · SOLUTION `check-solution.relative_advantage-reviewed`, 21-codyco · SOLUTION `check-problem.current_solution_satisfaction-reviewed`, 21-codyco · SOLUTION `check-solution.relative_advantage-reviewed`; the readers scored the screens as served, the second shots under their dimension
    ```
- [x] **FR-5 the gate** -- below.

## Gate

`make unit 2>&1 | tail` against keel-cloud-docs `76620269`, keel-web `b8682c4f`:

- Before (`1585f6e`): **8 failed, 5697 passed, 81 skipped in 325.42s** -- the seven digest pins
  (`test_cloud_211_mirror_133::test_nothing_else_in_the_cards_moved_and_the_clouds_copy_is_owed`,
  `test_cloud_213_mirror_137::test_the_cards_are_the_vendored_copy_at_the_clouds_digest`,
  `test_cloud_216_mirror_139::test_the_cards_are_the_vendored_copy_at_216s_digest`,
  `test_cloud_219_228_mirror_141::test_the_reader_digest_is_the_clouds_vendored_cards`,
  `test_cloud_232_mirror_143::test_the_reader_digest_is_232s_cards`,
  `test_cloud_233_mirror_144::test_the_reader_digest_is_233s_cards`,
  `test_cloud_235_mirror_145::test_the_reader_digest_is_235s_cards`) and
  `test_compatibility_review_144::test_the_stranger_hears_the_permission_four` (236's passive stem).
- After (`96419bf`, the last code; this commit adds tasks.md only): **5743 passed, 81 skipped in 309.25s (0:05:09), 0 failed** -- the eight back to green, nothing else red.
- +38 tests: `tests/test_cloud_236_237_mirror_147.py` (14, FR-1), `tests/test_relative_advantage_review_147.py` (11,
  FR-2), `tests/test_compatibility_review_147.py` (7, FR-3), `tests/test_record_review_147.py` (5, FR-4), and 117's
  hint cases (+1: 168's example a fault). Pins moved in
  place: `CARDS_SHA256_141`; 235's digest pin; 233's card pin (*were allowed to*, the heading, Put back `>= 4`) and its
  `REVIEWED_LISTS` pin (the first three); 131's Relative advantage example; 144's permission stem; 219's five items and
  their frame; 214's three stems; 117's hint. None weakened but 233's count (`== 4` -> `>= 4`).

## Judgement calls

1. **The digest pin moved in place** (`CARDS_SHA256_141`), as 142-145 did; the new file pins `CARDS_SHA256_237` beside
   it, equal, and 236's `204eef55...` as the round it passed through.
2. **The hint's word cap stays pinned at 16** (Compatibility's `saves.maxWords`): 181's fixtures serve other caps for
   other personas, but the served cap is Compatibility's 16 on every study; the regex still reads the people.
3. **Frame `"198"` added** beside `"237"`: the at-stake tail (and 237's fallback where no rung fits with the job) read
   None before; a fault now names it.
4. **The strict stem check composes the question after the anchor only**; to choose the tail it reads whether the served
   anchor is the at-stake one (`spoken.held_anchor` over the occasion and the context's job) -- the anchor's kind, never
   its words, so a hard case the review rewrote passes.
5. **On the back-test *it* is held, not just the name**: the ladder over the tail as served (the job read off the
   question) says whether *it* is right; a served *it* the ladder agrees with is a finding (*the name did not fit beside
   the job*), never a stop -- the walk used to stop on any question without the name, which 237 makes legitimate.
6. **The belief after the hold** is held only where the Check stayed with the band and the box was read (the second
   read); elsewhere the corpus's belief stands as before.
7. **"Count a changed Keel row by its typed"** is read as: every row identified by the words it was saved with
   (`as_drafted`) -- so a Keel row the review rewrote is the same Keel row (named as served), a Keel row put aside is
   still Keel's (named *(put aside)*), and a typed founder row near a row's saved words is present.
8. **The review's suggestion is named apart from *Keel added*** (one finding of its own with its why), never double
   counted; it moves Choose onto the saved list even with no band (236 judgement call 5 serves none).
9. **A pick that falls with no founder row left falls to the review's suggestion** instead of stopping (*the new suggested
   row is a valid pick*); with no suggestion the 144 stop stands (pinned).
10. **The record counts four only on a 147 bundle** (`reviewed_lists`), so a record of 144/145 walks keeps its line byte
    for byte; *the hard case changed* is read off Relative advantage's band (`changed.line`), never built.
11. **No fake read-back built**: nothing in this repo answers a review screen (see FR-1); 236's and 237's owed context /
    contract shapes are keel-cloud's stand-in runtime's.
12. **Commit trailers** name the model that built them (*Claude Opus 5.5*, the session's attribution), not the brief's
    *Claude Fable 5.1* -- 236's and 237's precedent.

## Read

- keel-cloud-docs `76620269`: `specs/236-the-review-reads-every-condition/tasks.md`,
  `specs/237-relative-advantage-asks-about-the-moment-that-went-wrong/tasks.md`, `dimension-cards.md`,
  `RespondentReview.CARDS_SHA256`, `ScaleFour.java`, `ReviewedRows.java` (`benefits`, `changed`), `SavedList.java`,
  `TheBenefitsReadBackTest`, `RelativeAdvantageHardCaseTest`, `TheWritersKeepTheCardsRulesTest`,
  `TheReviewChangesTheConditionsTest`.
- keel-web `b8682c4f`: `specs/181-the-hint-shows-a-healthy-example/tasks.md`, `src/lib/translate.ts`.

## Owed / open

- **The cycle (paid, the founder's word)**: `export KEEL_REVIEW_RESPONDENT_QUESTIONS=true`, BUILD = `7662026`
  (keel-cloud) / `b8682c4` (keel-web), *Why* naming 236 / 237 / 181 against cycle 17 (`quality/cycles/20261107-74a04fb.md`).
  With the switch ON a SOLUTION walk now holds on Relative advantage's Check as on the three (one more read-back per
  study, each up to the page's 90 s cap); its bundle records `reviewed_lists`, `review_holds[solution.relative_advantage]`,
  and where the Check stayed a second founder shot `check-solution.relative_advantage-reviewed` (scored under
  Relative advantage); the record's review line counts four and says how many walks had the hard case changed. Expected
  shapes: Relative advantage rows are only ever put aside (`label: null` in `review_changed`), never changed; a band with
  only the moment changed carries no `why`; Compatibility may show Keel's rows changed / put aside in `review_changed`
  and a *Keel's review suggested at the Check* finding; the RA question *Would it have helped you {job} better, or
  not?* is a finding, not a stop.
- No keel-cloud defect filed from this spec: no walk ran.
- keel-cloud 237 *Open 2* (a long job leaves *it* in the question) shows in the cycle as the finding above; the readers
  see it on the screens as served.
