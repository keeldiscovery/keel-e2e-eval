# Feature Specification: The Relay — Eval Framework

**Feature Branch**: `004-relay-evals`

**Created**: 2026-08-31

**Status**: Draft

**Input**: keel-cloud `canon/designs/relay-design.md` §12 (the required eval-framework spec),
with §§2, 9, 14 for context. Shipped contracts: keel-cloud `6f1c175` (relay endpoints), keel-web
`07745c2` (ChatPane), keel-skill `8610b04` (relay conduct, M15). This repo builds the eval side
only — keel-cloud/keel-web/keel-skill are never modified from here (gaps go to `runs/DRIFT.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A relay client and bridge exist in the harness (Priority: P1)

The harness gains a relay client (founder side: session-gated post/read/presence; agent side:
key-gated long-poll/post with lease handling) and a bridge loop utility that is the same
mechanical shape as the production host: poll, wake a reasoning callable once per founder turn,
post the reply. Browser page objects can read the chat pane (turns, kickers, playback tables,
composer, presence banner, thinking state).

**Independent Test**: a stackless unit test drives `harness.relay`'s client against a stubbed
HTTP layer (lease mint/renew/refuse, empty-poll vs turn-carrying poll) without a live stack.

**Acceptance Scenarios**:

1. **Given** a founder turn posted via the session, **When** the agent side long-polls, **Then**
   the turn is returned and a lease token is minted on first contact.
2. **Given** a second bridge polls while a lease is live, **Then** it is refused plainly and the
   first bridge is unaffected.

### User Story 2 - S-001..S-009's founder-conversation moments re-venue through the relay (Priority: P1)

The shared opening (`arrive_and_create`) and the founder-reply pattern speak via relay turns —
scripted reasoning (the existing `Scenario` payload builders already compute the founder-facing
text) posts the reply through the relay instead of only returning it from the protocol call. The
founder browser asserts the CREATE playback renders as a table in the chat pane (S-001) and one
clarification exchange round-trips visibly.

**Independent Test**: S-001 (and every other scenario via the shared recipe) opens the chat pane
after CREATE and finds the founder's turn and the agent's playback turn, table-rendered.

**Acceptance Scenarios**:

1. **Given** `arrive_and_create` runs, **Then** the chat pane shows the founder's opening turn and
   a playback turn for CREATE's own `recorded` object, rendered as a table (not raw text).
2. **Given** one clarification exchange (S-001's INTRODUCE_ASSUMPTIONS door), **Then** both the
   founder's line and the agent's reply appear in the chat pane in order.

### User Story 3 - S-011 proves the relay itself (Priority: P1)

A new scenario exercises what only the relay can prove: turn ordering under interleaving
(founder posts while the agent bridge is mid-poll), presence honest through an agent silence
(banner appears when the bridge stops, absent while it runs), a second bridge's lease refusal
reported plainly with the first bridge unaffected, and a payload-carrying playback turn rendering
as a table in the browser.

**Independent Test**: `make eval K=s011` runs standalone, scored, no LLM.

**Acceptance Scenarios**:

1. **Given** the founder posts a second turn before the bridge's poll returns, **When** the
   bridge's poll resolves, **Then** both turns are visible, founder-authored, in post order.
2. **Given** the bridge stops polling, **Then** the presence banner appears within the configured
   staleness threshold; **given** it resumes, **Then** the banner clears.
3. **Given** a second bridge attempts to poll while the first holds the lease, **Then** it is
   told so plainly and the first bridge's own poll/post cycle is unaffected.

### User Story 4 - The gauntlet re-venues onto the same plumbing (Priority: P2)

`founder_sim`'s turns go through the relay; `agent_session`'s loop becomes the bridge loop
driving `claude -p --resume` per founder turn. The same SHP facts and checks are computed from
stack state, unchanged — only the plumbing between founder simulator and agent process becomes
the shipped relay/bridge shape.

**Independent Test**: `make eval-shaping` still computes SHP-1..SHP-7 from `get_stage_card`;
`transcript.jsonl` now also carries the relay wire calls for the same conversation.

### User Story 5 - Policy v5 sweeps the chat surface (Priority: P2)

Rendered turn text and playback tables get the same CLARITY sweep every other founder-facing
surface gets; the presence banner's honesty gets an ORIENTATION check; the every-door-opens rule
extends to links inside agent turns.

**Independent Test**: `tests/test_policy_v5.py` (renamed from v4) seeds a failing and a passing
fixture per new check, construction-not-assertion, per every prior policy bump.

### Edge Cases

- A relay turn-cap refusal (house-voice remedy) must not be mistaken for a lease refusal.
- A bridge that never receives a founder turn within its poll window re-polls cleanly (no
  spurious lease loss, no wasted reasoning call).
- The gauntlet's `claude` CLI cannot itself poll the relay — the bridge feeds it founder turns
  exactly as before; only the relay carries the same turns in parallel (§12.3's "same facts, same
  SHP checks").

## Requirements *(mandatory)*

- **FR-001**: `harness/relay.py` provides a founder-side client (session-gated) and an agent-side
  client (key-gated, long-poll, lease mint/renew/refusal) matching keel-cloud's shipped contract.
- **FR-002**: `harness/bridge.py` provides a bridge loop utility: poll → per founder turn invoke a
  reasoning callable → post reply/playback; a lease refusal stops the loop and reports it, never
  contends.
- **FR-003**: `harness/browser.py` gains chat-pane page objects: turns (kicker, text, playback
  table), composer, presence banner, thinking state.
- **FR-004**: `evals/recipes.py`'s `arrive_and_create` and the founder-reply pattern speak through
  the relay; assertions on the protocol side are unchanged.
- **FR-005**: A new `evals/test_s011_relay.py` proves ordering-under-interleaving, presence
  honesty, lease refusal, and playback rendering; scored; an FID fact for a turn's text
  round-trip; no ledger note (no new journey moment).
- **FR-006**: `harness/agent_session.py`/`harness/founder_sim.py` re-venue onto the bridge/relay
  for the gauntlet's conversation carrier; SHP scoring is unchanged.
- **FR-007**: `evals/policy.py` bumps to v5: CLA over rendered chat text/tables, ORI for presence
  honesty, every-door-opens extended to agent-turn links; `tests/test_policy_v4.py` renamed to
  `test_policy_v5.py`.
- **FR-008**: `stack.toml` and `docker-compose.yml` gain a `playground` profile (own ports/volume)
  alongside the default eval profile; `make up PROFILE=playground` documented in README.
- **FR-009**: Product gaps discovered land in `runs/DRIFT.md`, never worked around in this repo.

## Success Criteria *(mandatory)*

- **SC-001**: `make eval-all` (S-001..S-011) completes scored runs in one session; S-011 included.
- **SC-002**: `make eval-shaping` runs once, real model, and still computes SHP-1..SHP-7 from
  stack state, now over the relay-carried conversation.
- **SC-003**: Stackless suite (`make unit`) stays green throughout, including new relay-client and
  bridge unit tests.
- **SC-004**: Policy v5's new checks are seeded and proven, additive (no existing check loosened).
- **SC-005**: The playground profile boots on its own ports/volume; an eval run under the default
  profile cannot touch it.

## Assumptions

- keel-cloud/keel-web/keel-skill are used exactly as shipped at the pinned commits named above;
  any mismatch with this design is a DRIFT.md finding, not a workaround here.
- The re-venue is pragmatic, not exhaustive: shared recipes carry the conversation through the
  relay; per-scenario protocol assertions are unchanged, per the design's own "carrier, not a
  rewrite" framing.
