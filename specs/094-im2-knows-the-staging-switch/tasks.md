# Tasks 094 -- IM2 knows the staging switch: the lock screen's one switch label is the screen's own words too

Branch `094-im2-knows-the-staging-switch` (worktree `wt/eval-094`), off master `6a2d4dd` (091 and 092 in;
`INTERVIEWER_MARKS_VERSION` 15). Built by Claude Opus 5.5 on 2026-10-30 (commits carry the hand-off's `Claude Fable 5.1`
trailer). Read only: keel-web **`aec26ec`** (`translate.ts` `recordAtLockSwitch`, `beforeInterviewerSub`;
`components/corridor/BeforeStep.tsx`, the switch's markup and the lock body; spec 132's tasks.md), keel-cloud
**`fcec4533`** (contract 49, `canon/openapi-v2.yaml`: `GroupArrival.interviewer`, `Interview.arrival`); keel-web spec
140's tasks.md (the pins for keel-e2e-eval 092). The spec of record (FR-1 to FR-3, and FR-1a / FR-2a added on master
`5da2739` mid-build; not edited). The two bundles the coordinator named, read from the main checkout's `runs/`:
`20261030T125356Z-s006-paidly` (IM2 on S3) and `20261030T130043Z-s017-open-link` (the arrival card). **No paid call, no `make eval`**: the lock journey never
runs against a `recordOnSend: true` server locally (the eval stack does not set `KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL`),
so the switch's shape is held by unit tests built from keel-web's source words, with the switch drawn (staging's shape)
and without (the local stack's). Nothing merged into master or deployed; the branch pushed after every commit, never
force-pushed.

| Commit | What |
|---|---|
| `06a098e` | FR-1: IM2 reads the switch's label; `INTERVIEWER_MARKS_VERSION` 15 -> 16 |
| `faf0c31` | FR-2: the lock step records the switch, left on, and the body's no flag |
| `63c0590` | merge of origin/master `5da2739` (the spec gained FR-1a and FR-2a) -- merged, not rebased (judgement call 9) |
| `630cf7d` | FR-1a: IM2 reads Send more's one credits note on S3 |
| `b64c276` | FR-2a: the open-link leg reads keel-web 140's card and intro |
| the docs commit | this file, `AGENTS.md`'s spec-094 paragraph |

## Unit (the gate)

`make unit` on the live checkouts (keel-cloud `fcec4533`, keel-web `aec26ec`):

| | passed | failed | skipped |
|---|---|---|---|
| master `6a2d4dd` (the hand-off's record) | 3,931 | 0 | 53 |
| branch at FR-1 (`06a098e`) | 3,945 | 0 | 53 |
| branch at FR-2 (`faf0c31`) | 3,960 | 0 | 53 |
| branch at FR-1a (`630cf7d`) | 3,968 (derived: its own run overlapped FR-2a's edits in the tree -- judgement call 12) | -- | -- |
| **branch at FR-2a (`b64c276`, the last code; the docs commit adds none)** | **3,970** | **0** | **53** |

The +39 are this spec's: `tests/test_im2_staging_switch_094.py` (32), five `SEEDED` IM2 cases, and two in
`tests/test_open_link_092.py` (140's words read off keel-web; the card on 140's face row).

## FR-1 -- IM2 accepts the switch -- `06a098e`

- [x] T001 `evals/interviewer_marks.py`: `LOCK_SWITCH_TESTID = "record-at-lock"` and `LOCK_SWITCH_LABEL`
  (`Record {face, one to three words} at lock · {n} credits`, keel-web 132 `recordAtLockSwitch(face, changePrice)`; the
  face picked, *the interviewer* before one is). `price_words_on("L1", ...)` now takes away, in turn, 091's one credits
  sentence and then the one switch label: a second of either is named (*a second switch: '...'*), a number in either
  not the served `changePrice` (`served`, else `fake.CHANGE_PRICE`, 400) is named, any currency anywhere on L1 is named,
  and any price word left outside both is named. With no switch drawn the loop finds none and L1 reads as v15. S1, S2,
  S3 read as before (the label there is a price word).
- [x] T002 `no_price_shown` (IM2) names the label it read (`L1 switch`, `None` where none is drawn) beside 091's
  `L1 credits sentence`.
- [x] T003 **`INTERVIEWER_MARKS_VERSION` 15 -> 16** with its v16 note.

| File | Old | New | Why |
|---|---|---|---|
| `evals/interviewer_marks.py` `INTERVIEWER_MARKS_VERSION` | 15 | 16 (+ the v16 note) | IM2 reads its record differently (FR-1) |
| `evals/interviewer_marks.py` `price_words_on` | L1: the credits sentence alone is the screen's | + the switch label, once, at the served price | FR-1 |
| `evals/interviewer_marks.py` `no_price_shown` detail | `L1 credits sentence` | + `L1 switch` | the label it read, named |
| `tests/test_interviewer_marks.py` card version, `test_controls_089`, `test_recorded_path_074`, `test_founder_walk_076`, `test_draft_list_minimum_091` | `INTERVIEWER_MARKS_VERSION == 15` | 16 | T003 |
| `tests/test_interviewer_marks.py` `SEEDED` IM2 | 091's L1/S1/S2/S3 faults | + a second switch (*Record Saskia at lock · 400 credits* after Daphne's), + a label at 900 | each FR-1 clause made to fail |
| `tests/test_im2_staging_switch_094.py` (new) | -- | keel-web's words read off the checkout (`recordAtLockSwitch`, the `record-at-lock` label, `role="switch"`, `checked={!recordOnSend}`, `lockOptional`); the pattern over *Daphne* / *Saskia* / *the interviewer*; IM2 without the switch (091's reading, `L1 switch` None) and with it (met, the label named); a pick and another served price; a second switch, another number, a currency, a label not keel-web's; the label off L1; the version and its note | the acceptance's unit test, both shapes |

## FR-1a -- IM2 accepts Send more's one credits note -- `630cf7d`

Why: journey s006 of 2026-10-30 faulted IM2 on S3 (`priced: {"S3": ["credits"]}`, bundle
`runs/20261030T125356Z-s006-paidly`): keel-web 131 drew one note under Send more's format rows, the first `.hint`
(`format-credits`), which 092 FR-4a already holds in the leg -- but IM2 v15 read every *credits* on S3 as a price.

- [x] T007 `evals/interviewer_marks.py`: `FORMAT_CREDITS_NOTE` (the pattern of keel-web 131's `FORMAT_CREDITS_NOTE`,
  *Each person who answers uses {n} credits, whichever way they answer.*); `price_words_on("S3", ...)` takes it away once
  and names a second note, a number in it other than the interview's price (`interview_charge.INTERVIEW_CREDITS`, 30),
  any currency anywhere on S3, and any price word left. The take-away is one helper, `_own_words`, shared with L1's
  sentence and switch (their faults' words unchanged). `no_price_shown` names `S3 credits note`. The v16 note says so;
  no second bump (judgement call 10).
- [x] T008 **The s006 bundle re-scored**: `marks.scorecard(interviewer.json)` at v16 -- IM2 met, the card **29 of 29**
  (it read 28 of 29 at v15, IM2 the one unmet), `S3 credits note` the note as drawn.

| File | Old | New | Why |
|---|---|---|---|
| `evals/interviewer_marks.py` `price_words_on` | S3: every price word | S3: Send more's one note taken away first, at 30 | FR-1a |
| `evals/interviewer_marks.py` `no_price_shown` detail | `L1 credits sentence`, `L1 switch` | + `S3 credits note` | the note it read, named |
| `tests/test_interviewer_marks.py` `good()` S3 | *AI interviewer · Saskia Text only Let them choose The interviewer is already recorded.* | + *Each person who answers uses 30 credits, whichever way they answer.* before the state line | S3 as keel-web 131 draws it |
| `tests/test_interviewer_marks.py` `SEEDED` IM2 | -- | + a second note, + the note at 45, + *About $0.12 each.* | each FR-1a clause made to fail |
| `tests/test_im2_staging_switch_094.py` | -- | +5: the note's words off keel-web and the harness (`ivs.FORMAT_CREDITS_NOTE`) at `INTERVIEW_CREDITS`; S3 exactly as s006 read it reads clean; S3 without the note as before; a second note / 45 / a currency / *400 credits* / *price* fault; the note on S1 or L1 is a price word | the acceptance's unit tests |

## FR-2 -- the lock journey leaves the switch on -- `faf0c31`

- [x] T004 `harness/vectors_screens.py`: `RECORD_AT_LOCK` and `record_at_lock_switch(face, credits)` (132's words);
  `Corridor.lock_switch(main)` reads the lock card's switch -- `{"drawn": 0}` where none is drawn, else `drawn` (the
  count), the first one's `label`, its checkbox's `role`, `on` (`is_checked`) and `disabled` -- and `Corridor.l1()` returns
  it as `switch`. Read only: nothing in the walk presses, checks or unchecks it. `word_pilot_and_lock` already reads `l1()`
  before the press and keeps the body sent (`l1["sent"]`), so `leg_lock`'s `j.screens["L1"]` now carries both.
- [x] T005 `evals/interviewer_leg.py`: `_lock_switch(j, record)`, the leg's **first** step (before the own-AI refusals,
  so it runs on both profiles): from `j.screens["L1"]` it records `record["lock"]` = the switch, the body sent, its
  `recordOnSend` keys by path (`lock_flags`, any depth: `interviewer.recordOnSend` or top-level) and IM2's reading of the
  label (`price_words_on("L1", label)`), and asserts at most one switch, a drawn switch on with `role=switch`, and **no
  `recordOnSend` in the lock body**. A leg handed no lock screen (a test double, a project locked off the page) records
  nothing. The module docstring's *Since spec 094* paragraph.
- [x] T006 Tests (+15, in `tests/test_im2_staging_switch_094.py`): keel-web's body builder read off the checkout (the flag
  only with the switch off, a fresh mount on); `Corridor.l1()` on static frames of 132's card in chromium -- the switch on
  (`{"drawn": 1, "label": "Record Daphne at lock · 400 credits", "role": "switch", "on": True, "disabled": False}`, the
  column's text glued *...face.Record Daphne at lock · 400 creditsDaphne...* and IM2 clean on it), absent (`{"drawn": 0}`),
  off (`on: False`); no `.uncheck(` / `.check(` / `.set_checked(` / click on the switch in the walk, the reader or the
  relock; the step's passes (on with `{expectedRevision, interviewer: {face}}`; none, with that body or own AI's
  `{expectedRevision}`; an `l1` read before 094 with no `switch` key) and its five refusals (off, the flag with the switch
  on, a flag with none drawn, two switches, no `role=switch`); `lock_flags`; `_lock_switch` before `_own_ai` before the
  remote return.

| File | Old | New | Why |
|---|---|---|---|
| `harness/vectors_screens.py` `Corridor.l1()` | title, sub, faces, carousel, button, text | + `switch` (`Corridor.lock_switch`) | FR-2: the switch recorded where it is drawn |
| `evals/interviewer_leg.py` `_leg` | `_own_ai` first | `_lock_switch` first, then `_own_ai` | FR-2, both profiles |

## FR-2a -- the open-link leg reads keel-web 140's card -- `b64c276`

Why: journey s017 of 2026-10-30 failed on stranger A's card (bundle `runs/20261030T130043Z-s017-open-link`): spec 092
was built against keel-web `e4f204e` (136, contract 48: no face on the card, the intro's who line the given name from a
browser note, *not you?* `/i/{group}`); keel-web 140 (master `aec26ec`, contract 49) draws *Daphne, Keel's interviewer,
asks the questions · about 10 minutes* with her still, and the intro's line from the arrival token's own
`Interview.arrival` -- the email and the absolute `groupUrl` -- with no press needed.

- [x] T009 `harness/browser.py`: `arrival_interviewer(minutes, name=None)` -- with a name, 140's
  `arrivalInterviewerAfterName` after it; without, 136's `arrivalInterviewer`; `arrival_signed_in(email)` (was the first
  name); `ARRIVAL_NAME` (`strong.iv-arrival__name`) and `ARRIVAL_FACE` (`span.iv-arrival__face`), read by `Arrival.read`
  as `interviewer_name` and `interviewer_face` (None / 0 on a text group); the greeting / who-line comment and the
  `Arrival`, `sign_in` and `intro` docstrings: drawn from the wire, no press, no browser note.
- [x] T010 `evals/open_link_leg.py`: `read_the_card` holds the row to the served `GroupArrival.interviewer` (its name in
  the words, the bold name, one still; 136's words and none when it is null); `read_the_intro` holds the who line to
  `arrival_signed_in(stranger.email)` and `not_you` to the served `Interview.arrival.groupUrl` as is, which must be
  absolute and end on the group's token; `Interview.arrival` is now required on the arrival's token (its email the
  stranger's) where 092 checked it only when present. The module docstring's step 2 follows.
- [x] T011 `tests/test_open_link_092.py`: re-pinned below; FR-2a's own two tests.

| File | Old | New | Why |
|---|---|---|---|
| `harness/browser.py` `arrival_interviewer` | `(minutes)`: *Keel's interviewer asks the questions · about {m} minutes* | `(minutes, name=None)`: + *{name}, Keel's interviewer, asks the questions · about {m} minutes* | keel-web 140 FR-1 |
| `harness/browser.py` `arrival_signed_in` | `(first_name)`: *... as Maya · not you?* | `(email)`: *... as maya.okafor@gmail.com · not you?* | keel-web 140 FR-2 |
| `harness/browser.py` `Arrival.read` | -- | + `interviewer_name`, `interviewer_face` | the card's face, read apart |
| `evals/open_link_leg.py` `read_the_card` | `arrival_interviewer(minutes)` | `arrival_interviewer(minutes, served face's name)`, + the name and the still | s017's fault |
| `evals/open_link_leg.py` `read_the_intro` | `who` *as {given name}*, `not_you` `/i/{group_token}`, `arrival` checked if present | `who` *as {email}*, `not_you` the served `groupUrl` (absolute, ending on the token), `arrival` required | keel-web 140 FR-2, contract 49 |
| `tests/test_open_link_092.py` `test_the_cards_words_are_136s` | `arrival_signed_in("Maya")` | `arrival_signed_in("maya.okafor@gmail.com")`, + the named and the null row | the words as 140 has them |
| `tests/test_open_link_092.py` `ARRIVAL_HTML` | 136's row only | a `ROW` slot: `ROW_FACE` (140's still, bold *Daphne*, the words after) or `ROW_NULL` (Keel's mark, 136's words) | both rows contract 49 serves |
| `tests/test_open_link_092.py` `INTRO_HTML` / the intro test | *as Maya*, `href="/i/gRoUp"`; `..._136_draws_it` | *as maya.okafor@gmail.com*, `href="http://localhost:5173/i/gRoUp"`; `..._140_draws_it` | keel-web 140 FR-2 |
| `tests/test_open_link_092.py` (new) | -- | `test_the_cards_words_are_keel_web_140s` (`arrivalInterviewerAfterName`, `arrivalInterviewer`, `arrivalSignedIn`, `ARRIVAL_NOT_YOU`, the face markup, `href={arrival.groupUrl}` off the checkout); `test_the_arrival_card_is_read_as_140_draws_it` | the pins read off keel-web |

## FR-3 -- nothing else moves

The other marks (IM1, IM3-IM30), 091's reading of the sub (the sentence's pattern and its faults, unchanged and taken
away first), the journeys' other steps (`leg_lock`, `_keels_door_l1`, `_own_door_l1`, the L1 revisit's no-price step:
untouched; `_keels_door_l1`'s recorded actual `{**l1, ...}` carries the new `switch` key on a back-test without a line
changed), `MARKS_VERSION` 23, the corpus, the scenario set (seventeen).

## Judgement calls

1. **"`evals/interviewer_leg.py`'s lock step" is a new step that reads the lock as `leg_lock` walked it.** The leg has
   no lock of its own: the project is locked earlier by `corpus_scenario.leg_lock` through
   `vectors_screens.Corridor.word_pilot_and_lock`, and keel-web 132 J-4 draws no switch once locked, so the switch can only
   be read at the press. The read is added to `Corridor.l1()` (one key, the harness), the record and the asserts to the
   leg's new first step `_lock_switch`, as the spec names. `leg_lock` and its two door steps are not touched.
2. **The flag is refused whether the switch is on or not drawn.** FR-2 names "when the switch is on"; 132's three states
   send the flag only with the switch off, which the journey never does, so on a server serving `recordOnSend: false`
   (the local stack) the body carries none either -- asserted too, the stronger reading of the same rule.
3. **`role=switch` is held on a drawn switch.** 132 T004's real checkbox with `role="switch"`; a label with no switch
   role is not the element the spec names.
4. **IM2 reads the label off L1's text, by pattern, not off the element.** IM2 scores `screens["L1"]`, the revisited
   screen's text (`l1_again`, which draws no switch after the lock -- 132 J-4); the element is read by test id where it is
   drawn, at the lock (FR-2). A second switch is a second label in the text. `textContent` glues the label to the sub's
   last word and to the first face's name, so the pattern takes no word boundary before *Record* or after *credits*; the
   same gluing means a made-up price word glued to the next element (*creditsDaphne*) escapes `PRICE_WORD`'s `\b` --
   true before this spec, named, not guarded (the tests close their made-up labels with a space).
5. **IM2 still reads the revisit, so on today's journeys the switch never reaches it.** S-005 / S-006 lock on the
   founder's own AI (no card, no switch, on either profile) and the remote profile skips the screens; IM2 v16 admits the
   label wherever an L1 text carries it (a stack that set the variable, a future walk of the lock text). The lock step's
   record is where staging's switch would show on a Keel's-door lock.
6. **The lock step's record names IM2's reading of the label** (`price words`, at the default 400: the leg reads no faces
   at lock) but does not assert it: FR-2 asks the switch, its state and the flag.
7. **A refused-then-relocked lock** (spec 070) keeps the first press's body (`l1["sent"]`); the relock is a fresh mount,
   where 132 draws the switch on, and the harness touches it neither time.
8. **`_lock_switch` runs before `_own_ai`**, so the remote profile records it (the six's lock on staging) before its
   early return; a journey double with no `screens` (the remote-scorecard test) records nothing.
9. **origin/master `5da2739` was merged, not rebased.** The coordinator asked for a rebase; FR-1 and FR-2 were already
   pushed and the brief forbids a force-push, so `63c0590` merges it (clean: it touched only `spec.md`). Nothing of either
   side lost; the branch rebases clean onto master if one is wanted at merge time.
10. **FR-1a rides v16, no 17.** FR-1a lands before anything was merged, so IM2's reading moved once on this branch; the
    v16 note names both readings (the switch, the note).
11. **The note's number is the interview's fixed 30, not a served price.** FR-1a names 30 (*the interview price*); the
    harness's `interview_charge.INTERVIEW_CREDITS` is that price (keel-cloud's charge table), and the wire serves the
    note no number, so 30 is the one number admitted.
12. **FR-1a's gate count is derived.** Its `make unit` run overlapped the FR-2a edits being written into the same tree
    (4 failed: 092's fixtures read mid-edit), so it was not used; the final tree's run (3,970 / 0 / 53, after both) is
    the measured one, and FR-1a's own line is FR-2's 3,960 plus its eight cases.
13. **FR-2a: `groupUrl` is held as served, and to its shape.** The leg compares *not you?*'s href to the served
    `Interview.arrival.groupUrl` and holds that it is absolute (`http(s)://`) and ends on the group's token, not to a
    url the harness builds (the participant base is the cloud's to choose; contract 49: *the same string as the
    founder's `GroupRow.url`*).
14. **FR-2a: "no press needed" is written down, not walked anew.** keel-web 140 draws the greeting and the who line from
    the arrival's own read; the leg's browser strangers still press *Continue with Google* (that is how they sign in)
    and C still signs in on the wire. No new step opens C's token in a browser: the spec names the leg's card and intro
    asserts and the fixtures, and those follow.

## What did not hold

- **Nothing was walked on a stack**: no stack sets `KEEL_V2_INTERVIEWER_LOCK_RECORD_OPTIONAL`, so the switch is held by
  static frames of keel-web 132's card and by doubles; `make eval K=s005` / `s006` (the leg's new first step records
  `{"drawn": 0}` and the own-AI body there) and the remote six on staging are the coordinator's.
- **s006 and s017 were not re-walked**: the s006 bundle's IM2 is re-scored at v16 (met); s017's fixes are held by static
  frames of 140's card and intro and the words off keel-web; `make eval K=s006` / `K=s017` are the coordinator's.
- **On staging the six lock on the founder's own AI** (S-005 / S-006 `own_ai_door`), where 132 draws no switch; the
  switch shows only on a Keel's-door lock (the back-tests), which run no interviewer leg -- there it is recorded in
  `j.screens["L1"]["switch"]` and `_keels_door_l1`'s step, unasserted.
