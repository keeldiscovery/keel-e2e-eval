# Spec 093 -- The harness mirrors keel-cloud 161: the bare phrase, the follow-up rung, the stale L1 and L5 restatements

keel-cloud 161 (merged 2026-10-30, cloud master `b009fac8`, contract unchanged at 47): the Current solution phrase is
the bare act (*working out what the baby needed*), a stored *your way of ...* phrase is read bare by one helper
(`ItemFrames.bare`), a drafted phrase that opens on *your way of* gets rule `L1` (one repair turn, then read bare), the
follow-up rung reads *You said {phrase} works for you. What keeps it working?*, the belief sentence keeps *their way of
{bare}*; `solution-mechanism.md`, `asked.md` and `founder-lists.md` were cut under budget with every rule kept; the
compatibility item's rules are 20 words framed, *you / your* in every clause, and `suggested` never on Adoption
friction -- **and keel-cloud's L5 has admitted a `suggested` on Compatibility since keel-cloud 121 FR-3** (the founder's
"Agree.", contract 31, the Choose screen's pre-pick); the harness's *Purchase friction only* is a stale restatement.
161's tasks.md lists the pins.

## Rules

- **FR-1 The scripted phrase is bare.** `harness/vectors_script.py` (918-920) drafts the Current solution phrase bare
  (the corpus's *your way of ...* read with the opening stripped, as the cloud's helper does); no scripted PROBLEM draft
  earns an `L1` note; `tests/fixtures/registry/slice.yaml` (167) and the spoken tests (`test_instruction_spoken.py`
  186-188, 216-217) carry the bare phrase; `tests/test_controls_089.py` (322) reads the registry as 161 wrote it.
- **FR-2 The rung.** `harness/interviewer_fake.py` (271-272), `tests/test_follow_up_ladder.py` (286) and
  `tests/test_follow_ups_075.py` (122) say 161's rung.
- **FR-3 The harness's own rules say the cloud's.** `instructions/score.py`: L1 (305-307) in 161's words; L5 (330-332)
  admits `suggested` on Purchase friction AND Compatibility, never elsewhere (the cloud's rule since 121), so the
  founder-lists screen of 2026-10-29 stops faulting the Lullaby listening item for it; `MARKS_VERSION` moves if a mark's
  reading moved, with its note.
- **FR-4 Nothing else moves.** The corpus (revision 19), the frames (089/090), the marks beyond L1/L5, the readers.

## Acceptance

`make unit` green with ZERO failed; the founder-lists screen's bundle of 2026-10-29 (`runs/20261029T193750Z-instructions`)
re-read shows no L5 fault on `solution.compatibility`; on the local stack at cloud `b009fac8`, `make eval K=s005` green
with no `L1` note in the journey. Build after 090 (the same builder may take 090 then 093). Build on the founder's word
of 2026-10-30.
