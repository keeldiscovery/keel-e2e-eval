# The Eval Set — Design

**Status**: Proposed. Downstream of `eval-scoring-design.md` (the scoring machinery this set
runs on) and of keel-cloud's `canon/journeys.md` and `product-constitution.md` — the
scenarios below are those documents' moments turned into executable, scored discoveries. Where a
scenario and the journey disagree, the journey wins; where the journey and the shipped server
disagree, the server is reported (DRIFT), not worked around.

## 1. What the set must cover

S-001 (built) proves the sunny day. The journeys' load-bearing moments are everything S-001
never touches: the pricing claim that dies and is replaced (§1.7–1.9), the founder who goes
ahead against the evidence (§1.10), the divided person counted honestly on both sides (§1.7),
the interviews full of opinions that move nothing (§1.7 "nothing solid yet"), the stranger whose
link died under them (§2.4), the stranger who declines or skips everything (§2.1–2.2). Each of
those is a scenario below; each runs fully scored under the policy.

## 2. Policy v2 first — one recalibration, recorded not buried

The v1 policy swept `instruction.content` and `requirements` with the founder-language yardstick
(CLA-A1/GUI-A2). The shipped contract says otherwise: those texts are addressed to the **agent**
— methodology and payload guidance that legitimately name `CONTRADICTED`, `askedOf`,
`goingAhead` — and the founder never receives them raw. The founder-exposed protocol surface is
the handoff `display`; the founder-exposed rendered surfaces (UI, participant page) already have
their own sweeps and scored clean.

Policy v2 therefore: CLA-A1/GUI-A2 sweep `display` only among protocol texts; `requirements`
keep their presence/sentence-shape checks (GUI-A1); `instruction.content` is not vocabulary-
swept. POLICY_VERSION → 2; DRIFT #4 re-adjudicated ("policy category error, not product text
bug"); `eval-scoring-design.md` §3 gets the amendment. The twenty v1 failures disappear because
they were mismeasurement — and the claim stays checkable because the UI/participant sweeps that
would catch real founder-facing leakage remain at full strength.

## 3. The scenarios

Each is one module on the Scenario base, fully scored, with its own fact registry. Assertion
lists name the journey section they enforce.

**S-002 — the pricing pivot** (§1.7, §1.8, §1.9, §2.4). Commercial deal-breaker ("they would
pay annually, upfront") driven to ruled-out by three participants; problem/solution driven
supported. Then: agent offered FRAME replacement on the commercial stage; carries only the
budget-owner belief (evidence never spoke against it); new claim + new assumptions arrive
unapproved; founder re-approves in the browser; a fresh link carries only fresh pricing
questions plus the still-open problem belief — **nobody is re-asked what is settled**; a second
participant answers; commercial recovers; brief. Asserts: old claim struck-through-but-readable
on the commercial card; problem/solution cards untouched (statuses, counts identical before and
after); the pre-pivot link, opened after the reframe, shows §2.4's out-of-date page and the
participant's fifteen minutes are refused up front; a participant who already submitted is never
told their work was wasted.

**S-003 — going ahead anyway** (§1.10). Same ruined pricing claim, but this founder does not
reframe. Agent asks for the brief: first submit carries no `goingAhead` → the server refuses
(A9) and the refusal's remedy tells the agent what the founder must supply; the founder's own
sentence is then carried and the brief renders the GOING AHEAD ANYWAY box first, with the
disproved belief in "what the evidence said no to" — never blurred into "taking on faith".
Asserts the refusal-first path deliberately: the warning conversation is the product moment,
and the eval walks it rather than skipping to the happy submit.

**S-004 — the divided person** (§1.7, Marcus). One participant gives concrete evidence in both
directions on one belief; another gives one-sided evidence; a third gives wishes. Asserts: the
divided person appears under both "counted for" and "counted against"; the collapsed line
counts **people, not quotes**; the wish lands in "said, but didn't count" with its plain-words
reason; verdict math follows people-counted rules (aggregate r7).

**S-005 — opinions move nothing** (§1.7 "nothing solid yet"). All participants answer every
question with preferences and speculation; one skips every question outright. Asserts: beliefs
stay unsettled with the "people gave opinions rather than examples" explanation surfaced;
the all-skipped submission is handled gently end to end (whatever layer refuses or accepts it,
the stranger sees a kind page and the founder's counts stay honest); a skipped answer is
information, not an error.

**S-006 — the stranger declines, the stranger consents** (§2.1–2.3). One invitee opens the
link and clicks "No thanks" — asserts the decline is graceful, nothing reaches the founder as
an answer, and the invitations screen never shames anyone. Another consents by starting,
answers, and the thank-you page promises nothing the product cannot keep (name relayed, no
deletion promise, no account creation). Consent-screen fidelity: who is asking, what about,
how long, where the words go — all four present, nothing more.

**S-007 — the wire pushes back** (protocol negatives; no browser). Unknown screen → refusal
listing the five; ungranted handle → rule `context`; stale token after a concurrent commit →
rule `concurrency`, facts preserved on retry; every refusal carries actionable
`{rule, problem, remedy}` and the token survives payload faults. Scored on agent-surface
attributes only; its GUIDANCE checks measure whether the *remedies* would tell a lost agent
what to do — refusal text is part of the founder's experience once removed.

## 4. What the set does not attempt tonight

PIVOT/STOP terminal scenarios (journey has no UI moment for them beyond calm terminality — one
assertion inside S-007's get_state checks suffices for now); multi-role links spanning stages
beyond what S-002 needs; load or soak. Recorded, not forgotten.

## 5. Five passes

1. **Journey-fidelity pass**: every scenario names the journey sections it enforces, and the
   two hardest sentences in the journeys each got an assertion rather than a paraphrase —
   "nobody is asked a question the evidence has already settled" (S-002's link contents) and
   "a person who has already submitted is never told their work was wasted" (S-002's post-
   pivot check on the answered link).
2. **Adjudication pass**: re-read the shipped `ActionSchemas.requirements` and the failing v1
   checks before designing more checks on top of them — which reclassified finding #4 from
   product bug to policy category error and produced §2, instead of an eval set that would
   have inherited twenty false positives into every scenario.
3. **Discovery-honesty pass**: where the journey and the shipped server may disagree (gentle
   all-skipped handling, decline behavior, strikethrough rendering), the scenario asserts the
   *experience* and lets the run discover the mechanism — findings become DRIFT entries and
   low scores, and the user authorized fixing what's glaring, so the loop is
   run → fix → rerun, recorded per repo.
4. **Independence pass**: each scenario creates its own project and owns its own participants;
   S-002 and S-003 share a setup shape (ruined pricing) but not state — the going-ahead
   conversation must not depend on pivot machinery having run.
5. **Cost/coverage pass**: seven scenarios ≈ the full journey surface at one overnight run's
   cost; the cut list (§4) is explicit so absence reads as chosen, not missed.

## 6. Open decisions

1. Whether S-007's scored attributes should feed the same run-score aggregate as browser
   scenarios — yes, but its scorecard marks the absent categories as not-applicable rather
   than 0, so the aggregate stays honest.
2. Strikethrough detection (S-002): assert on accessible text + styling hook, not pixel
   inspection.
