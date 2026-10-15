# Tasks 043

- [x] T001 baseline: `make unit` 1,857 passed / 53 skipped; `make eval K="s005 or s006 or s007"` 3 passed against
  keel-cloud-docs `7850360` + keel-web `da0b9eb` with nothing changed (contract 15 broke no page object)
- [x] T002 `harness/contacts_fake.py`: the fake restated (59 people, 53 with an email; the UK 27, the US 26), charge v8
- [x] T003 `stack/ledger.py`: reads (account by `sub`, ledger rows since, balance, the database clock); stand-ins 1-3,
  `psql -v` variables only, remote refused
- [x] T004 `evals/contacts_marks.py`: CM1-CM14, unmeasured never passed, the scorecard
- [x] T005 `evals/contacts_leg.py`: `leg_contacts` steps 1-18 (spec FR-002), `leg_contacts_not_b2b`, DRIFT #83's step,
  the 068 follow-up named
- [x] T006 `Journey.stack` / `founder_identity`; S-005 and S-006 extras call the legs
- [x] T007 `tests/test_contacts_marks.py` (every mark met on a good record, each failed on a seeded fault; the fake
  against keel-cloud's fixture; the stand-ins' shape); `make unit` green
- [x] T008 `make eval K="s005 or s006 or s007"` 3 passed, twice, with the leg, against `7850360` + `da0b9eb`
- [x] T009 `runs/DRIFT.md` #83; AGENTS.md; README.md; spec.md
- [ ] T010 (waits for keel-web 068) page objects for the Contacts tabs, the dataset page, the Send more popup and the Sent
  register, held to the wire the leg holds (`contacts_leg.WEB_068_FOLLOW_UP`)
