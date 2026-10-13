# Tasks 039

- [x] T001 spec, plan, tasks
- [x] T002 `harness/vectors_script.py`: the script from r9 (seven screens, four RESPONDENT_QUESTIONS aliases), the keys
      table derived from keel-cloud's export, the founder's inputs, each person's answers by code, the id codec, the cost
      re-expressed over the asked period, `people_to_invite`
- [x] T003 `harness/vectors_screens.py`: corridor, People popups, interview, board / vector pages / brief
- [x] T004 `evals/corpus_scenario.py`: one function per leg, `open_journey`, strict and live; S-005/6/7 with their vectors
      extras
- [x] T005 the journey on the wire against the local stack until r9's standings matched (D-1..D-4, DRIFT #74), then every
      leg on keel-web's screens with the wire kept as the assertion (DRIFT #75)
- [x] T006 S-012 leg two on the same legs (`strict=False`); its dry tests and the keel-door tests moved; classic-only helpers,
      `harness/stranger_stories.py` and their tests deleted
- [x] T007 stack: keel-web's framework plugin in `stack/vite.eval.config.ts`, `KEEL_VECTORS_ENABLED`; S-002 reads its
      fixture lazily; S-004 keeps its own classic `STAGES`
- [x] T008 `tests/test_vectors_journey.py` (33): the script, the composed words against keel-cloud's rules, the keys
      table, the founder, the people, the scenario's shape
- [x] T009 AGENTS.md, README.md, runs/DRIFT.md #74 #75
- [x] T010 `make unit` 1,705 passed / 53 skipped (was 1,764 / 75); `make eval K="s005 or s006 or s007"` 3 passed against
      keel-cloud-docs `b8a4eed` + keel-web `e54cb1c`
- [ ] T011 (not here) S-012 live through a host on the vectors leg; S-001, S-002 and S-004 are still classic and go with
      classic; DRIFT #74's fix in keel-cloud moves S-005's Frequency to NOT_ASKED_YET
