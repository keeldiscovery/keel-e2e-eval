# Spec 058 -- The four interviewers in the marks and fixtures

Against keel-cloud 110 (contract 23) and keel-web 087. Builds on 051/054 (IM marks, the remote profile). Build lean:
one `make unit` plus one stack run of the journey that locks and records.

## Rules

- **FR-1 Codes.** Every fixture, scenario and mark that names JUDY/JIN/ANNA/DAPHNE/TITO moves to LIVIA (where JUDY was)
  and the four; the face evaluators read the four; `FACE_UNKNOWN` still expected for an old code.
- **FR-2 Mark IM28 *tap to hear*.** On Lock's last step, a tap on an unpicked card picks it and a `video` inside that
  card plays to its end (≤ 8 s) and the still returns; the picked face is the one posted at lock. On the remote profile
  the end is awaited with the 90 s navigation timeout.
- **FR-3 Mark IM29 *the respondent hears her*.** On the intro when the founder let them choose, *Hear <name>* plays
  her hello and the still returns; the choice buttons stay enabled throughout.
- **FR-4 Marks file.** The two rows; CHANGELOG; `MARKS_VERSION` as the house rule says.

## Acceptance

1. Unit: the two evaluators' tables.
2. Stack: the locking journey green with IM28–IM29 on chromium, web from the 087 worktree.
3. `make unit` green: the count on master plus the additions, measured.
