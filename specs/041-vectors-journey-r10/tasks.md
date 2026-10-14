# Tasks 041

- [x] T001 vectors_script: CALIBRATION_QUESTIONS lists per list dimension + Prevalence's event and fifths; one entry per
  job in corridor order (`calibration_jobs`)
- [x] T002 vectors_script: RESPONDENT_QUESTIONS the gate's clause only (E1-E4, `GATE_EVENTS`); ASKED from the corpus's
  faces; BRIEF headline + three answers citing what broke; ladder / rank / chip readers and RESPONDENT_ESCAPES deleted
- [x] T003 vectors_script: typed inputs -- Answer words, saved lists, picked index; picks on the wire's positional codes;
  "nothing" as 0; the story chip CANT_RECALL
- [x] T004 vectors_screens: 063's frame (counter, dots, locked nav), single screens, Answer / Check and save / Choose,
  S2, step 5's two screens
- [x] T005 vectors_screens: 064's idea screen, gate, items (pick two, fixed answers, one escape last), reveal; each
  screen recorded; the stage page's per-person list
- [x] T006 corpus_scenario: legs re-pointed; DRIFT #74 wire step dropped; codes mapped in leg_standings; brief on the wire
  (cards, broke, pilot); the respondent screens held to the wire
- [x] T007 S-005 / 006 / 007 extras re-read for r10
- [x] T008 the 24 call-89 skips un-skipped and green; `make unit` 1,846 passed / 53 skipped (was 1,818 / 77)
- [x] T009 S-012 leg two on the same legs (`strict=False`); its dry tests green (S-012 itself is live and not run)
- [x] T010 local stack: `make eval K="s005 or s006 or s007"` 3 passed against keel-cloud-docs `7b151f9` + keel-web
  `c499bf7` (before 065 landed)
- [x] T011 runs/DRIFT.md (#74 observed live; #78, #79, #80, #81), AGENTS.md, README.md, spec.md
- [x] T012 keel-web 065 (merged as `844ea36` while this spec was in flight): page objects for the brief's page one
  (`/p/{id}/brief`: decision, how sure, headline, four tiles the fourth the pilot, per stage question / answer / cards,
  the next tests, the footer), page two (`/p/{id}/brief/breakdown`: one block per card, *What broke*, the way back), the
  download's tab and the overview's third tile; held in `leg_brief` and `_board` to the wire `leg_brief` already reads
- [x] T013 the three journeys re-run green, twice, against keel-cloud-docs `7b151f9` + keel-web `844ea36`
