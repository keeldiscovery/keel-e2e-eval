# Tasks: The Relay — Eval Framework

**Input**: spec.md, keel-cloud specs/projectv2/relay-design.md §12 (+ §§2, 9, 14 for context)

## Phase 1: Setup

- [X] T001 Research the three shipped contracts (keel-cloud relay endpoints, keel-web ChatPane
      DOM, keel-skill relay section) live from source — record exact wire/selector contract
      before writing any client code

## Phase 2: Foundational — the relay client and bridge

- [X] T002 `harness/relay.py`: founder-side client (session-gated post/read/presence) and
      agent-side client (key-gated long-poll, lease mint/renew/refusal) + stackless unit tests
      against a stubbed transport
- [X] T003 `harness/bridge.py`: the mechanical bridge loop (poll → per founder turn invoke a
      reasoning callable → post reply/playback), lease-refusal → stop-and-report + unit tests
- [X] T004 `harness/browser.py`: chat-pane page objects (turns/kickers, playback tables, composer,
      presence banner, thinking state)

## Phase 3: US2 — scenario re-venue (P1)

- [X] T005 [US2] `evals/recipes.py`: `arrive_and_create` posts the founder's opening line via the
      relay and runs one bridge cycle so CREATE's own commit plays back as a relay turn; assert
      the chat pane renders it as a table
- [X] T006 [US2] `evals/test_s001_smoke.py`: one clarification exchange (the existing
      INTRODUCE_ASSUMPTIONS door) round-trips visibly through the chat pane
- [X] T007 [US2] Document exactly how far the re-venue reaches (recipes-only carrier vs. every
      scenario's own assertions) in this tasks.md's own completion note

## Phase 4: US3 — S-011 proves the relay (P1)

- [X] T008 [US3] `evals/test_s011_relay.py`: turn ordering under interleaving, presence honest
      through an agent silence, lease refusal for a second bridge, payload-carrying playback
      renders as a table; scored; one FID fact (a turn's text round-trip); comment noting no
      ledger entry (no new journey moment)

## Phase 5: US4 — gauntlet re-venue (P2)

- [X] T009 [US4] `harness/founder_sim.py` turns post through the relay; `harness/agent_session.py`
      loop becomes the bridge loop driving `claude -p --resume` per founder turn; SHP facts/checks
      unchanged (`evals/test_shaping_gauntlet.py`)

## Phase 6: US5 — policy v5 (P2)

- [X] T010 [US5] `evals/policy.py` → v5: CLA over rendered chat text/playback tables, ORI for
      presence-banner honesty, every-door-opens extended to agent-turn links
- [X] T011 [US5] [P] `tests/test_policy_v4.py` → `tests/test_policy_v5.py`: keep v4 fixtures,
      construction-not-assertion fixtures for every v5 addition

## Phase 7: Split stacks

- [X] T012 [P] `stack.toml` + `docker-compose.yml`: a `playground` profile (own ports/volume);
      `make up PROFILE=playground`; README documents it; default eval profile unchanged

## Phase 8: The closing gate

- [ ] T013 `make down && make up` (rebuild from source); `make eval-all` (S-001..S-011); `make
      eval-shaping` once (real model); record every verdict/score; gaps → runs/DRIFT.md;
      stackless suite green throughout

## Dependencies

T001 → T002–T004 (parallel once T001 lands) → T005–T007 → T008 → T009 (parallel with T008) →
T010 → T011 → T012 (independent, parallel-safe anytime after T001) → T013.

## Re-venue scope (T007)

Pragmatic, not exhaustive, per the design's own "carrier, not a rewrite" framing:

- **All nine of S-001..S-009** inherit the relay carrier through the one shared recipe,
  `evals.recipes.arrive_and_create`: CREATE's own founder line and its `recorded` playback (flat
  `{name, problem}` scalars — confirmed live never to render a `<table>`) now travel the relay for
  every scenario that calls it, with no change to any scenario's own protocol-side assertions.
- **S-001 alone** gets targeted chat-render assertions beyond the shared carrier: INTRODUCE_ROLES's
  own commit (`{"roles": [...]}`) is driven by hand and relayed as a playback turn, asserted to
  render as an actual `<table>` in the ChatPane (the design's "CREATE playback renders as a table"
  ask, corrected by live evidence to the one commit in this opening sequence that actually can);
  and one clarification exchange ("What happens once I approve this card?" / the agent's answer)
  round-trips visibly, asserted present and in order.
- **S-002..S-009** get the carrier only — no scenario-specific chat-render assertion was added to
  them; their own protocol/browser assertions are entirely unchanged.
- **S-011** is the one scenario that exercises the relay's own mechanics directly (ordering under
  interleaving, presence honesty, lease refusal, a second payload-carrying playback table) rather
  than through the shared recipe's carrier alone.
- **The gauntlet** (`test_shaping_gauntlet.py`) relays every turn once a fresh project id is first
  observed mid-conversation (the relay cannot address a project that does not exist yet, and this
  gauntlet's own opening turns predate CREATE by design) — the handful of pre-CREATE turns are
  never retroactively relayed.
