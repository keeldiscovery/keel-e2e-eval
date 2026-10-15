# Plan 043

1. Baseline: `make unit` and `make eval K="s005 or s006 or s007"` on the worktree as it stands against keel-cloud-docs
   `7850360` + keel-web `da0b9eb` -- does contract 15 (the register's new fields, newest first) break a page object?
2. `harness/contacts_fake.py`: keel-cloud's `FakeContactSource` restated over its own fixture (sizes, pages in fixture
   order, the excluded), and the charge table v8 (`CONTACT_PAGE` 150, `CONTACT_EMAIL` 12, their Starter-rate costs).
3. `stack/ledger.py`: the ledger and the account read off the local Postgres; the three named stand-ins (Keel's door
   with a fresh grant, the low balance, the door reversed); the remote profile refused.
4. `evals/contacts_marks.py`: CM1-CM14 over a contacts record; `CONTACTS_MARKS_VERSION` 1.
5. `evals/contacts_leg.py`: `leg_contacts` (S-006, on the wire, last) and `leg_contacts_not_b2b` (S-005); the record and
   the scorecard into the bundle; DRIFT #83 stepped round; `WEB_068_FOLLOW_UP`.
6. `evals/corpus_scenario.py`: `Journey.stack` / `founder_identity`; S-005's and S-006's extras call the legs.
7. `tests/test_contacts_marks.py`; `make unit`.
8. The local stack: `make eval K="s005 or s006 or s007"` twice with the leg.
9. Docs: `runs/DRIFT.md` #83, AGENTS.md, README.md, this folder.
