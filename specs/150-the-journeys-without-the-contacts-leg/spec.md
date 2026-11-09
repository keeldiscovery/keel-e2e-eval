# Spec 150 -- The journeys without the contacts leg

keel-web 185 removes the Contacts and Keel-managed sub-pages (the founder, 2026-11-09: Sent alone). The scripted
journeys S-005 and S-006 walk the contacts leg (`evals/contacts_leg.py`, `evals/contacts_marks.py`,
`harness/interviews_screens.py`'s Contacts and dataset screens, `harness/contacts_fake.py`), and the guide marks read the
contacts frames. After 185 those screens do not exist.

## Rules

- **FR-1 The leg goes.** `contacts_leg` and `contacts_marks` are removed; S-005 and S-006 send their links by the Sent
  page's *Send more* (OWN or GROUP) and by the wire where they did so already; `harness/interviews_screens.py` loses the
  Contacts and dataset screens; `harness/contacts_fake.py` stays only if a journey still seeds people through the
  cloud's contacts endpoints (the fake contact source the cloud routes eval founders to) -- the builder says which.
- **FR-2 The marks.** `CONTACTS_MARKS_VERSION` is retired (no row of MARKS_VERSION, as its header says); the report's
  marks and the interviewer's marks that cite a contacts card drop it; `guide_marks` drops the contacts frames' cues
  with keel-web 185's frame counts.
- **FR-3 The redirects.** A journey that opens `/interviews/contacts` or `/interviews/managed` asserts the redirect to
  Sent (one test).
- **FR-4 The record.** `backtest.py` and the cycle record stop counting a contacts step; nothing else moves.
- **FR-5 Tests.** `make unit` green; the journeys' dry runs (`DRY=1`) green against the mirrors; no paid run.

## Out of scope

The cloud's endpoints (keel-cloud 244); any paid run.
