# Spec 075 -- The harness follows keel-cloud 139–142 and keel-web 122–124

The founder's morning of 2026-10-27 produced six product specs; this one moves the harness with them. Keel-cloud
139: a B2B money-only study lists no *has the problem* kind on the Interviews page or the contacts picker. 140: the
Price step's cost box names hours and rate (*40 to 80 hours a month at $80 an hour, $3,200 to $6,400 a month*).
141: Ability to pay's belief reads *Keel reads …*, never *You said …*, with a counting sentence under it. 142 +
keel-web 124: up to two follow-ups, each asked on the answer it hangs on under the kicker *About that*; the end
keeps *One last thing* for what is still owed; `followUps[]` on the response; contract 41. Keel-web 122: Plans,
Terms and Privacy rewritten; 123: the cost step's *Per* and *of* pre-filled with helper lines and the rate field
always shown when hours are priced. REVISION unchanged (the corpus is 16); marks change only where named.

## Rules

- **FR-1 The follow-up marks.** IM25 (the follow-up's windows: two minutes, four seconds) and IM27 (the follow-up
  after the answer against) are re-pinned to the new order: a follow-up asked right after its item under *About
  that*, at most two, *One last thing* only for an owed rung at the end; each pin's why names this spec. The AI
  walks that press *End* inside the follow-up's hold (S-005) press it inside the first on-the-spot follow-up instead,
  and the pilot-ask assertion of 074 holds there. The scripted respondents' answers that go against the founder are
  counted so each walk meets at least one on-the-spot follow-up and S-005 meets two; the corpus facts that read
  `followUp` read `followUps[]`.
- **FR-2 The founder's screens.** The money-only walk (S-016) asserts one kind card on Sent and one kind in the
  contacts picker; the cost-step walk reads the pre-filled *Per* and *of* and the rate field with its default note,
  and the Price step's cost box in 140's words; the Ability to pay stage-page read accepts *Keel reads* and asserts
  the counting sentence; any mark that read *You said* on that line is re-pinned and says why.
- **FR-3 The public pages.** The landing/plans checks (if any read the plans' numbers or the legal pages' sentences)
  follow keel-web 122's words; the matrix's smoke of `/terms` and `/privacy` (if any) reads the new *Last changed*.
- **FR-4 Nothing else moves.** The noise check, the six journeys' scripts beyond the lines above, the judge, the
  paid commands.

## Acceptance

`make unit` green; the six journeys green on the local stack against the merged checkouts (cloud through 142, web
through 124), then on staging after the deploy. Marks table in tasks.md: every pin moved, its why. No DRIFT filed
silently: a product behaviour the walks find that none of the six specs asked for is filed in `runs/DRIFT.md`.
