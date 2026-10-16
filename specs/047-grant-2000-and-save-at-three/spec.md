# Spec 047 -- The grant is 2,000 and Importance's Save waits for three

Two of the founder's decisions of 2026-10-16, mirrored by the referee: keel-cloud 098 (the free grant is **2,000**, for
everyone; existing 1,500 grants raised by 500 in V48) and keel-web 071 (Importance's Check screen disables Save below
three in all; the server's `ONE_MORE_NEEDED` is the backstop). **Scope: keel-e2e-eval.** Marks versions unchanged.

## Rules

- **FR-1** `harness.agent_host.KEELS_AI_GRANT` and `stack.ledger.GRANT_CREDITS` are 2,000; S-012 asserts `2,000 credits
  available` and `creditsAvailable` 2000 on the Google door; the stand-ins top the balance up to 2,000.
- **FR-2** On Importance's Check screen with one other named (01-countly), the journey asserts the one-more ask, **Save
  disabled**, and no PUT; the founder types the rest through *+ Write a difficulty they'd recognise*; the ask is gone,
  Save is enabled and one PUT carries the list. With two named (05-paidly), Save is enabled at once as before.
- **FR-3** FM2 is unchanged (own item plus the named, the typed appended, three at least).

## Acceptance

1. `make unit` green.
2. `make eval K="s005 or s006 or s007" PROFILE=remote` green against staging with keel-cloud 098 + keel-web 071.
