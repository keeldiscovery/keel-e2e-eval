# Spec 088 -- The harness reads one charge per interview: Begin posts, 30 credits land, readings cost nothing, an inactive link says so

keel-cloud 156 (merged 2026-10-30, cloud master `68ff142a`, contract 45; the credits design, amendment 2026-10-29): one
`INTERVIEW` row of 30 credits is written when a person presses Begin (`POST /v2/i/{token}/interview/begin`, written once
per invitation, never refused); `INTERPRET` and `THEMES` are priced 0; a link opened on a balance below 30 is served
`{state: INACTIVE, message: "This link is no longer active."}` and a begun link is served whatever the balance;
`InferenceCharge.VERSION` is 12. keel-web 131 posts Begin from the intro screen and shows the inactive page. The
harness pins the old prices and never presses Begin on the wire.

## Rules

- **FR-1 The prices.** `PRICE_VERSION = 12` in `harness/interviewer_fake.py` and `harness/contacts_fake.py`; the
  recording-pair mark (`evals/interviewer_marks.py`) reads it as today. Every figure that sums the old prices moves:
  `evals/test_s012_journey_through_a_host.py`'s five-participant total (readings 0, Begin 30 each, the rest as it
  was), the `creditsAvailable` deltas in `evals/interviewer_leg.py` and `evals/contacts_leg.py` (a reading no longer
  costs 10; a story's reading and the themes write their rows at 0), each re-pinned with why.
- **FR-2 Begin on the wire.** The browser journeys press Begin on the intro (`harness/browser.py`), which from keel-web
  131 posts the charge; the scripted path (`harness/vectors_script.py`, which posts the response directly) posts
  `interview/begin` before the response so a scripted person is charged as a real one is. A journey asserts, after one
  person's Begin, one INTERVIEW row on the ledger (`stack/ledger.py` returns every kind) of -30 with
  `idempotency_key interview:<invitationId>`, and that a second Begin on the same link writes none.
- **FR-3 The inactive link.** One journey (S-012's host, or a new short one) grants a founder a balance below 30 (the
  stack's ledger helper), opens a fresh link, and asserts the INACTIVE body on the wire and the one line on the page
  (keel-web 131: *This link is no longer active.*, no number, no *credits*); then raises the balance and asserts the
  link serves; then begins it, drops the balance again, and asserts the begun link still serves. The gallery's
  recorded expectations gain nothing (no example walks an inactive link).
- **FR-4 Decided before.** `quality/decisions.toml`: no entry names 156 (the credits were the founder's own design, not
  an advice row); nothing to mark.
- **FR-5 Nothing else moves.** The six remote journeys' assertions beyond the credits line; the quality cycle (the
  walk's founders are on Keel's AI with a fresh grant, so every link is active); the noise check.

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them); on the local stack at
cloud `68ff142a` or later and web at 131 or later, `make eval K=s012` green with FR-2's and FR-3's assertions, and
`K=s005` green (one Begin, one row). Build on the founder's word (the overnight run of 2026-10-29), after web 131 merges
(FR-2's browser press needs it; FR-1 and the scripted post can go first and tasks.md says which).
