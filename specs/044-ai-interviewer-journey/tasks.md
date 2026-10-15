# Tasks 044

- [x] T001 baseline green on the merged cloud + web, nothing changed: `make unit` 1,912 passed / 53 skipped; `make eval
  K="s005 or s006 or s007"` 3 passed (391 s) against keel-cloud-docs master `47dd816` + keel-web master `df2e97a`
- [x] T002 ledger rows + refusal codes in the harness; `price_version` 9 (`harness/interviewer_fake.py`; `stack/ledger.py`'s
  stand-ins keyed per spec and `recording`; `contacts_fake.PRICE_VERSION` 9; CM12 reads `INTERVIEWER_NOT_READY`)
- [ ] T003 page objects for L1, W1, S1/S2/S3, the popup, try, the stage and the sheet; the speech seam driver
- [x] T004 `interviewer_marks.py` IM1-IM12 + unit tests (each met on a good record, each failed on a seeded fault)
- [ ] T005 `interviewer_leg.py` steps 1-9; S-006 full, S-005 short
- [ ] T006 `make unit`; `make eval K="s005 or s006 or s007"` twice; DRIFT entries; docs
- [x] T007 the journeys after keel-cloud 095 (read on arrival; keel-cloud-docs master `a0b3759` = 095 worktree `ee86d1e`):
  the reading step door-aware (Keel's door presses nothing and waits for the newest batch, a founder's `POST readings`
  409 `READING_IN_PROGRESS` / `NOTHING_TO_READ`; the own door with the agent connected first keeps asking on the wire,
  095 call 14); IM13 (every reading / brief HOLD says why: `read-on-arrival:<id>`, `brief:after-batch`, `retry:<n>:<p>`,
  at most three attempts); the leg reads what Keel's keyless door left unread before it ends (call 152); DRIFT #84
  resolved; S-005/006/007 3 passed vs `a0b3759` + keel-web `df2e97a`
