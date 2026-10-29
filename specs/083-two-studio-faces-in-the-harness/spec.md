# Spec 083 -- The two studio faces in the harness: Daphne and Saskia, the four photo faces retired

keel-cloud 143 (keel-cloud-docs `f7b0e051`, **contract 44**, on master `f48f256e`) retired the four photo faces of
keel-cloud 110 (LIVIA, JIA, MARIEKE, CHUKWU) and offers two studio faces, DAPHNE and SASKIA; keel-web 125 (`786d4c3`)
draws them, ships `public/interviewer/faces/{daphne,saskia}.{webp,mp4,-poster.webp}` and the landing's two round
faces. The harness still mirrors keel-cloud 110: `harness/interviewer_fake.FACES` is the four, `PRESELECTED` LIVIA,
`RETIRED` the five of 094 (DAPHNE among them -- 143 FR-1 supersedes 094's DAPHNE with a new studio look, so DAPHNE is
offered again). Since 143 merged, `tests/test_interviewer_marks.py::test_the_faces_are_keel_clouds_own` is red on
master (3,667 / 1 / 53 at `a9e5e65`), and the six remote journeys cannot pass the interviewer leg against staging
cloud `f48f256` + web `786d4c3` (`evals/interviewer_leg.py` ~436 asserts the served faces are `fake.FACES`).

The marks, the readers, the rubric (version 2), the quality cycle and `REVISION` 17 do not move except as FR-3 says.

## Rules

- **FR-1 The fake is keel-cloud 143.** `FACES = ("DAPHNE", "SASKIA")`, `FACE_NAMES` Daphne / Saskia, `PRESELECTED =
  "DAPHNE"`; `RETIRED` = 094's five less DAPHNE plus 110's four (`JUDY, JIN, ANNA, TITO, LIVIA, JIA, MARIEKE, CHUKWU`), a
  pick of any 422 `FACE_UNKNOWN`; `helloUrl` of a retired face on a recording is null (143 FR-4) -- the fake serves a
  recording that carries a retired face as keel-cloud does. `preview_path` / `hello_path` unchanged (the two ship as
  `daphne.*` / `saskia.*`). `HELLO_MAX_S` holds (both hellos are 4.6 s). The comment block names 143 and the date.
- **FR-2 The leg and the journeys.** `evals/interviewer_leg.FIRST_FACE` becomes the face the founder picks for the first
  recording that is not the preselected one (SASKIA, as CHUKWU was to LIVIA); every served-faces assertion, popup
  words (*Record Saskia*), persona line and S1 words read the two from the fake, never a literal; the pick-a-face walk
  with the retired ones off the popup. S-005 / S-006 (and any journey whose words name a face) pass on the local stack
  against keel-cloud `f48f256e` + keel-web `786d4c3`.
- **FR-3 The marks.** `evals/interviewer_marks.py`: the face check (~911) and the name lines (~926, ~945) read the
  fake; if any mark's WORDS change, `INTERVIEWER_MARKS_VERSION` 12 -> 13 and the RUBRIC / marks changelog says why;
  if only the data moves, the version holds and tasks.md says so. `tests/test_interviewer_marks.py::
  test_the_faces_are_keel_clouds_own` reads keel-cloud's enum as today and is green against `f48f256e` (the enum lists
  the two first, then the retired four: the test reads the OFFERED ones -- match on the enum's offered flag or the
  first two, say which in tasks.md). `tests/test_interviewer_screens.py`, `tests/test_founder_feedback_073.py` fixtures
  that carry a face move with it.
- **FR-4 Nothing else moves.** The quality cycle, the readers, the back-tests' people and scopes (082), the report
  marks, the corpus.

## Acceptance

`make unit` green with ZERO failed (master `e8f2751`: 3,668 passed / 1 failed / 53 skipped -- the one red is this
spec's). S-005 green on the local stack (`make up`, `make eval K=s005`, `make down`; the stack from the keel-cloud and
keel-web checkouts as they stand: `f48f256e` and `786d4c3`); S-006 if it names a face. No paid command. tasks.md in
082's shape. Build on the founder's word -- given 2026-10-28 (the faces decision of 2026-10-27, the to-do list of
2026-10-28): the remote six cannot run on staging without it.
