# Tasks 083 -- The two studio faces in the harness: Daphne and Saskia, the four photo faces retired

Branch `083-two-studio-faces-in-the-harness` (worktree `wt/eval-083`, `.git` a file), off master `50f82b8` (the spec on
top of `e8f2751`). Read only: keel-cloud-docs `f48f256e` (`InterviewerFace.java`, spec 143's spec.md and tasks.md:
DAPHNE and SASKIA offered, the four photo faces retired as constants, `helloUrl` null on a retired face, 422
FACE_UNKNOWN on a retired pick), keel-web `786d4c3` (spec 125: `daphne.*` / `saskia.*` shipped, the retired four's
files kept, the picture band the retired four's only). `INTERVIEWER_MARKS_VERSION` 12, `MARKS_VERSION` 21, rubric 2,
`REVISION` 17 unchanged. **No paid call**: no back-test, no reader, no quality target, no API key. Nothing merged or
deployed; every commit pushed to the branch (the founder's rule of 2026-10-28).

| Commit | What |
|---|---|
| `c7c463a` | FR-1: `harness/interviewer_fake.py`; the fake's mirror test, keel-web's files test |
| `32e2d8b` | FR-2: `evals/interviewer_leg.py`; `test_the_legs_two_picks_read_the_fake` (+1) |
| `9347475` | FR-3: `evals/interviewer_marks.py` (changelog line only), `test_the_faces_are_keel_clouds_own` on the flag, the fixtures (`tests/test_interviewer_marks.py`, `tests/test_interviewer_screens.py`, `tests/test_founder_feedback_073.py`'s comment, `harness/interviewer_screens.py`'s comment) |
| this commit | this file, `AGENTS.md` (the 083 paragraph, the S-006 line's faces), `README.md` (the S-006 line's faces) |

## Unit

| | passed | failed | skipped |
|---|---|---|---|
| master `e8f2751` / `50f82b8`, keel-cloud checkout at `f48f256e` | 3,668 | 1 | 53 |
| `9347475` (FR-1..FR-3), same checkouts | **3,670** | **0** | 53 |

The one red of master, `test_interviewer_marks::test_the_faces_are_keel_clouds_own`, is green; +1 is the new
`test_the_legs_two_picks_read_the_fake` (3,668 + 1 red turned green + 1 new = 3,670). `make unit` 182 s.

## FR-1 -- the fake is keel-cloud 143

- [x] T001 `FACES = ("DAPHNE", "SASKIA")`, `FACE_NAMES` Daphne / Saskia, `PRESELECTED = "DAPHNE"`.
- [x] T002 `RETIRED` = `RETIRED_110` (`JUDY, JIN, ANNA, TITO`: 094's five less DAPHNE, retired by 110, not constants) +
  `RETIRED_143` (`LIVIA, JIA, MARIEKE, CHUKWU`: still constants) -- the spec's eight in the spec's order; a pick of any
  is 422 `FACE_UNKNOWN` (`REFUSAL_STATUS` unchanged).
- [x] T003 `served_hello(face)`: the `helloUrl` keel-cloud serves -- the hello of an offered face, `None` for a retired
  face a recording carries (143 FR-4, `InterviewerPlayer.Face`). `preview_path` / `hello_path` and `HELLO_MAX_S` (8 s;
  both hellos 4.68 s) unchanged. The comment block names 143, contract 44, `f48f256e` and 2026-10-28; the module
  docstring says two since 143.
- [x] T004 Tests: the fake's mirror (`test_charge_v9_and_the_fixed_lines`: the two, their names, the eight retired, the
  served hello of SASKIA and of LIVIA); keel-web's files (`test_the_hear_words_and_the_four_hellos_are_keel_webs_own`):
  a hello for the two, a still for all ten, no hello for `RETIRED_110` -- 143's four keep theirs on keel-web (125 FR-3
  deletes nothing; keel-cloud serves their `helloUrl` null).

## FR-2 -- the leg and the journeys

- [x] T005 `FIRST_FACE = next(f for f in reversed(fake.FACES) if f != fake.PRESELECTED)` -- SASKIA, the last card that
  is not the preselected one, as CHUKWU was to LIVIA; `CHANGED_FACE = fake.PRESELECTED` -- DAPHNE, a change and not the
  default. No face literal left in the leg.
- [x] T006 The step words that named the four: the first-recording step (*the two faces with their stills and hellos,
  Daphne preselected, ... a retired one (Judy)*) and L1 revisited (*the two faces, one checked*) read the count
  (`fake.number(len(fake.FACES))`), the preselected name and the retired pick from the fake. Every served-faces
  assertion, the popup's faces and *Record Saskia*, the persona lines (S1-S3), the Let-them-choose intro and the change
  already read `fake.FACES` / `FACE_NAMES` / `FIRST_FACE` / `CHANGED_FACE`.
- [x] T007 IM30's expected hello in the leg's record is `fake.served_hello(FIRST_FACE)`.
- [x] T008 Test: `test_the_legs_two_picks_read_the_fake` -- the two picks, and no `"SASKIA"`, `"DAPHNE"`, `"Saskia`,
  `"Daphne`, `"LIVIA"`, `"CHUKWU"` or *the four faces* in the leg's source.
- [x] T009 The journeys on the local stack (keel-cloud-docs `f48f256e`, keel-web `786d4c3`), below.

## FR-3 -- the marks

- [x] T010 `evals/interviewer_marks.py`: IM28's face check (`face in fake.FACES`), IM29's and IM30's names
  (`fake.FACE_NAMES`) and IM30's retired branch (`fake.RETIRED`) already read the fake. **No mark's words changed, so
  `INTERVIEWER_MARKS_VERSION` holds at 12**; the changelog carries a *v12 kept (spec 083)* line saying only the data
  moved (as *v5 kept (spec 055)* did).
- [x] T011 `test_the_faces_are_keel_clouds_own` **matches on the enum's offered flag**, not the first two: each
  constant's last argument; the `true` ones in order are `fake.FACES`, the `false` ones `fake.RETIRED_143`;
  `PRESELECTED = DAPHNE;`; each offered face's display name; no constant for `RETIRED_110`. Green against `f48f256e`.
- [x] T012 Fixtures moved: IM28-IM30's records and fault tables on SASKIA (the first pick; glyphs on the one unpicked
  card) and DAPHNE (preselected, the change; *another card*, *another name*, *another clip*), the retired-face fault
  CHUKWU (was TITO); the S1-S3 words and wire views of `good()`; IM30's retired-face test on TITO and CHUKWU, each with
  `served_hello` (None); `test_interviewer_screens.py`'s templates on Daphne; `harness/interviewer_screens.py`'s comment.

## FR-4 -- nothing else moves

- [x] T013 The quality cycle, the readers, the rubric, the back-tests' people and scopes (082), the report marks
  (`MARKS_VERSION` 21), the corpus (`REVISION` 17), `instructions/marks.py` (its *four interviewers* line is v20's
  history and stays).

## The acceptance

| Command | Result |
|---|---|
| `make unit` | **3,670 passed, 0 failed, 53 skipped** (182 s) |
| `make up` | all gates passed (keel-cloud-docs `f48f256e`, keel-web `786d4c3`) |
| `make eval K=s005`, run 1 | **red** 407 s: IM28 and IM30 -- SASKIA's hello fired `playing` and never advanced (`currentTime` 0, no `ended` in 20 s); see *What did not hold* |
| `make eval K=s005`, run 2 (local `--disable-audio-output`, not committed) | **green** 344 s (`duration_s` 342.3), interviewer marks v12: 23 measured, 23 met |
| `make eval K=s006` (same local flag) | **green** 383 s (`duration_s` 380.8), interviewer marks v12: 29 measured, 29 met; Saskia recorded first and her hello heard to its end, unmuted, in the card, the intro and the band (IM28-IM30); the change popup *Record Daphne* over DAPHNE, SASKIA, the change READY on DAPHNE |
| `make down` | done |

S-006 runs the full interviewer leg (its persona lines, popup, intro and change name the face), so it was run.

## Judgement calls

1. **The flag, not the first two.** The enum carries `offered` as each constant's last argument; reading it is what
   keel-cloud's own `OFFERED` reads, and survives a third face or a reorder. The test also pins the retired four on
   `false` and 110's four as non-constants.
2. **`RETIRED` split in two.** keel-web keeps 143's four's hellos (125 FR-3) but never had 110's; one tuple could not
   say both, so `RETIRED_110` and `RETIRED_143` compose the spec's eight, in the spec's order.
3. **The retired pick stays `RETIRED[0]` (JUDY).** The leg's 422 check is unchanged (still a code keel-cloud refuses);
   143's own refusal of a retired *constant* is covered by keel-cloud's `InterviewerJourneyTest` (LIVIA 422), and the
   harness's marks table now carries CHUKWU as the retired fault.
4. **`FIRST_FACE` computed, not written.** *Read from the fake, never a literal*: the last card that is not the
   preselected one -- SASKIA today, and the rule that made CHUKWU the pick under 110.
5. **The 073 band fixture keeps LIVIA.** keel-web 125 keeps 087's picture band for the retired four only (the two draw
   their 9:16 render with no band); a band on DAPHNE would be a page that does not exist. A comment says why.
6. **The marks version held.** Every face word in a mark is read from the fake at run time; no rule's words changed.

## What did not hold

- **S-005's first run on this laptop was red, for the machine.** Headless Chromium on this Mac fires `playing` for an
  unmuted `<video>` and its clock never moves: a probe on the running stack (`/interviewer/faces/{chukwu,saskia,daphne,
  livia}.mp4`, plain `chromium.launch()`, unmuted) stalled every face at `currentTime` 0 -- CHUKWU too, which ended in
  5.2 s on 2026-10-24's S-006 -- while the same clip muted, or unmuted with `--disable-audio-output`, played 4.68 s to
  `ended`. The audio output is stalled, not the files or the faces (all four mp4s are H.264 High 3.1 + AAC, `moov`
  first). S-005 and S-006 were then run with `--disable-audio-output` added locally to `evals/conftest.py`'s
  `chromium.launch` and the file restored before any commit; **the committed harness launches as before**. The marks
  still hold *sound on* (`muted` false on the media events): the flag only gives Chromium a fake audio sink.
- Not done: the remote six on staging (no deploy, no remote run in this spec's brief).
