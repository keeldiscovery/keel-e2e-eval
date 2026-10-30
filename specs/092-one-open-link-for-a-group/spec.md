# Spec 092 -- One open link for a group: the journey, with three strangers signing in with Google

The design: keel-cloud-docs `canon/designs/open-link-design-2026-10-29.md` with its amendment of 2026-10-30 (Google
sign-in on a group link). The cloud side is keel-cloud 162 (contract 48); the web side keel-web 136. This is the
harness's side: one journey, the stub issuer serving strangers, the register's By group tab read.

## Rules

- **FR-1 Strangers on the stub issuer.** `stack/stub_oidc` already registers identities (`POST /identities`) and
  accepts any redirect URI; the journey registers three strangers (sub, email, name, given_name) and signs each in on
  the group link's arrival page through the browser (`harness/browser.py`: press *Continue with Google*, pick the
  identity on the stub's picker as `sign_in` does for a founder) and through the wire (`stack/auth.py`: a
  `sign_in_arrival(group_url, identity)` that follows start → authorize with `identity=` → the participant callback →
  the arrival's own `/i/{token}`).
- **FR-2 The journey.** One new journey (`evals/test_s015_open_link.py`, or a leg of S-005 if the coordinator's stack
  budget prefers it: tasks.md says which): the founder on Keel's AI with a fresh grant makes a group link from Send more
  (*A group, with one open link*, the group named, the format *Let them choose*), copies it; stranger A signs in,
  begins (one INTERVIEW row of -30 on the ledger, `stack/ledger.py`), answers, ticks the pilot box; stranger B signs in,
  begins, pauses after the gate; stranger C signs in and never begins; A opens the link again and is served
  ALREADY_ANSWERED; B opens it again and continues where they were; the founder's Sent page shows By group · 1 with
  the group's section, the counter *2 of 20 answered*-shape line as the design words it, three rows (A answered, B
  opened not finished, C opened the link) each with the email under the name, *See answers* on A; the founder closes
  the link and a fourth stranger is served INACTIVE; reopen serves it again; the brief's Pilot view carries A's email.
  The ledger shows exactly two INTERVIEW rows (A, B; C never began). The journey never prints an email of a real
  person: the strangers are the stub's.
- **FR-3 The register read.** `harness/interviews_screens.py` reads the two tabs (*By name*, *By group*), the study
  line, a group section's heading, counter, Copy link / Close link / Reopen, and the per-group `LinksTable` with the
  same `td[data-label]` cells as today plus the stacked email; `Interviews.send_group(name, format)` makes one.
- **FR-4 The marks and the walk.** No mark moves; the quality walk's founders make no group link (the readers score the
  Send more screens as today, with the third choice drawn). The gallery records nothing new.
- **FR-5 Nothing else moves.** The named and dataset legs, the credits mirror (088), the controls (089/090).

## Acceptance

`make unit` green with ZERO failed; on the local stack at keel-cloud 162 and keel-web 136, the journey green; the
remote profile refuses it (the stub issuer is local; on staging the real Google client serves the participant callback
-- the coordinator registers the callback URI in the Google console before the remote journey is attempted, and the
remote run of this journey is NOT part of the remote six). Build after keel-web 136. Build on the founder's word of
2026-10-30.
