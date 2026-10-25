# Spec 071 -- Study scopes in the harness: ALL on every seed, two short journeys, the exporter's scope

Design of record: keel-cloud `canon/designs/study-scopes-design-2026-10-25.md` (§5, §9, §11, §15); keel-cloud spec
133 (contract 38: `scope` on the project create request and view; `GateItem.counts`; `Reveal.problem`;
`StandingsView.question`, `.ship`, `.gateFact`; out-of-scope vectors absent); keel-web specs 109/110.

## Rules

- **FR-1 ALL on every seed.** The golden seven and the fourteen back-tests create their projects with `scope: ALL`
  (the harness's own scope, never offered by the web); the corpus revision stays 16; every mark, mirror and golden
  number unchanged. The walk sends `scope` in the create request as the web will; the corridor's screens are
  unchanged under ALL (the choose screen is walked by picking nothing: the harness creates through the API as
  today — the choose screen is covered by the two new journeys).
- **FR-2 S-015, a problem-only journey** (short): a seed derived from Countly with `scope: PROBLEM` — the choose
  screen walked in the browser (the problem card, Continue), Context, the problem chat and its four calibrations,
  Ready, lock; one link; the stranger walks the gate + story + part 1 and meets the thank-you (no pilot box); the
  Overview reads *Should you build it?*, no Pilot tab, no tiles, one card, a one-piece ship; the decision words Build
  / Not yet by the rule; marks on each.
- **FR-3 S-016, a money-only journey** (short): a seed derived from Countly (B2B) with `scope: COMMERCIAL` — the
  choose screen (the money card), Context, the problem chat, the idea card (*Your idea*), Who decides, the money
  calibration, lock; **only the decision-maker's link** is issued; its interview opens with the reveal's `problem`
  sentence then the idea card then part 3; the Overview reads *Will they pay?*, Pilot + What they would pay tiles,
  one card, a one-piece ship; marks on each; the harness's spoken mirrors apply to the reveal's sentence.
- **FR-4 The back-test host door takes `--scope`** (default ALL) and records it in `backtest.json`; the judgement
  register row gains the scope in its stack column when not ALL.
- **FR-5 The gallery export carries `scope`** on each index row (from the run's `backtest.json`), `ALL` for the
  fourteen; the attribution check accepts the five values.
- **FR-6 Nothing else moves**: marks v20, REVISION 16, the golden numbers.

## Acceptance

Unit on the create request's scope, the two seeds' expected walks (stubbed), the host door's flag, the exporter's
row. Journeys S-005/006/007/014 green and the two new ones green on the local stack (keel-cloud spec 133 merged,
keel-web spec 109 merged).
