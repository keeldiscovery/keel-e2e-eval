# Tasks 058

Built against keel-cloud-docs master `b54c349` (110, contract 23) and keel-web 087 **as built in parallel** in
`wt/keel-web-087` (read-only; its working tree on `f7758f7`). The test ids are 087's own: `face-hear` (the play glyph
on an unpicked card with a hello), `intro-hear` (*Hear <name> · 5 s*), the card's `video.pcard__clip` and the intro's
`video.pface-hello__clip` (`hidden` while not playing), `data-hearing` on the card.

- [x] T001 FR-1: `harness/interviewer_fake.py` `FACES` = LIVIA, JIA, MARIEKE, CHUKWU, `PRESELECTED` LIVIA, `RETIRED`
  (the five), `hello_path`, `HELLO_MAX_S` 8; the leg's `FIRST_FACE` CHUKWU (Tito's place, the last card),
  `CHANGED_FACE` LIVIA (where JUDY was); `GET interviewer/faces` held to `helloUrl` too; a retired code (JUDY) posted
  is 422 `FACE_UNKNOWN` and charges nothing, beside BOB; fixtures, README, AGENTS.
- [x] T002 FR-2 / FR-3 page objects (`harness/interviewer_screens.py`): `HEAR_JS` (a capture listener for every
  `video`'s media events + a 100 ms poll of the choice buttons), `hear_card`, `Persona.record(hear_s=)`,
  `Player.hear(wait_s=)`; the wait is 20 s locally, the 90 s navigation timeout on the remote profile
  (`HEAR_WAIT_REMOTE_S`).
- [x] T003 FR-2 / FR-3 marks (`evals/interviewer_marks.py`, **`INTERVIEWER_MARKS_VERSION` 6**): IM28 `tap_to_hear`
  (`hear_face`), IM29 `the_respondent_hears_her` (`hear_intro`); IM28 owed on the short form (S-005) too, IM29 on the
  full leg (S-006: the Let-them-choose link is its).
- [x] T004 FR-4: `MARKS_VERSION` stays 20 (no screen schema, instruction or corpus moved; the house rule):
  `instructions/marks.py` gains the Spec 058 paragraph; the journey ruler's changelog in its own file.
- [x] T005 Acceptance 1: `tests/test_interviewer_marks.py` -- the good record carries both, 20 IM28 faults and 17 IM29
  faults (each fails its mark alone), one IM28 table row; `tests/test_interviewer_screens.py` -- the two ids, the
  words and the four hellos (the five stills kept, no hello for them) against keel-web's files (skip before 087).
- [x] T006 Acceptance 2 / 3: the stack and `make unit` (below).

## Judgement calls

1. **IM28 is measured in the persona line's *Record the interviewer* popup**, not on Lock's last step: no journey
   locks on Keel's door with a carousel (the corpus founders are on their own AI, so L1 is one line; spec 044 call
   148), and the first recording of a project locked before it is `POST interviewer/face` from that popup -- the same
   `FaceCarousel`. "The face posted at lock" is that POST's `{face}`.
2. **"Plays to its end"** is the page's own media events: a `playing` with `muted` false on the served `helloUrl`,
   then an `ended` with the clock at the duration (within 0.25 s), the duration and playing->ended both 8 s or less,
   no media error, no other card's clip playing; "the still returns" is the card's / intro's clip not laid out and its
   `role=img` still laid out after the end.
3. **"Enabled throughout"** is a 100 ms poll of *Talk to* / *Answer in writing* from the tap to the end, plus a read
   before and after: every poll both enabled.

## Measured (2026-10-20)

**Stack, S-006 paidly** (`COMPOSE_PROJECT_NAME=keel-e2e-eval-058`, cloud 18082 / web 5183 / oidc 18092, postgres 55432;
keel-cloud-docs `b54c349`; **stack.toml's `keel_web` pointed at `../keel-web-087` for the run and put back, not
committed**): `make eval K=s006` **1 passed in 329 s** on the first run (`runs/20261020T212812Z-s006-paidly`),
chromium. Interviewer marks v6 **28 of 28** measured met (IM12 unmeasured as before, DRIFT #86).
- `GET interviewer/faces`: LIVIA, JIA, MARIEKE, CHUKWU, LIVIA preselected, each `helloUrl` `/interviewer/faces/<code>.mp4`;
  BOB and JUDY both 422 `FACE_UNKNOWN`, nothing charged.
- IM28: in *Record the interviewer*, Chukwu unpicked with her glyph (Jia, Marieke, Chukwu each carry one; Livia picked),
  the tap: `play` 52 ms, `playing` 59 ms, sound on, `chukwu.mp4`, `ended` 5,443 ms at 5.24 s of 5.24 s (played
  5,384 ms), no other card played; after it the clip hidden, the still back at once, Chukwu alone checked, posted
  `{face: CHUKWU}`.
- IM29: the Let-them-choose intro's *Hear Chukwu · 5 s*: `playing` 79 ms, sound on, `ended` 5,496 ms (played 5,417 ms),
  the round still back at once; *Talk to* and *Answer in writing* enabled before, after and on all 55 polls.

**`make unit`** (keel-web at the 087 worktree, ports put back): **2,795 passed / 53 skipped** against master's
2,717 / 53 (+78: 37 hear faults as seeded rows and 37 again as alone-tables, 1 IM28 table row, 3 keel-web 087 file
checks). Against keel-web master the three 087 checks skip.
