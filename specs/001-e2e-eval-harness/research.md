# Research: E2E Eval Harness

## 1. Driver transport
**Decision**: HTTP agent surface (`/v2/agent/**`) via `requests`; one `/mcp` reachability check.
**Rationale**: keel-cloud parity-tests MCP against HTTP; a Python MCP client is a dependency
with no added proof. **Alternatives**: MCP streamable-http client (revisit later); raw sockets (absurd).

## 2. Browser↔API origin
**Decision**: eval-owned `vite.eval.config.ts` with `server.proxy: {"/v2": "http://localhost:18080"}`,
launched as `npx vite --config <this repo's file>` from the keel-web checkout.
**Rationale**: keel-cloud has no CORS config and keel-web's api base defaults to same-origin —
proxying reproduces the deployed shape and touches neither repo (design pass 2).
**Alternatives**: add CORS to keel-cloud (product change from the eval repo — forbidden); VITE_KEEL_CLOUD_API_BASE cross-origin (fails without CORS).

## 3. Process lifecycle
**Decision**: spawn gradle/vite with `start_new_session=True`, record pgids in `runs/.stack/`,
health-gate by polling (any HTTP status beats connection-refused), teardown via `killpg` then
`docker compose down`.
**Rationale**: gradle spawns a tree; killing the parent alone leaks a JVM (design pass 5).
**Alternatives**: docker-izing keel-cloud/keel-web (slow rebuild loop, hides the dev-shaped stack the user actually runs).

## 4. Health gates
**Decision**: Postgres: `pg_isready` in-container; keel-cloud: HTTP poll on 18080 until any
response (budget 120s — gradle cold start + Flyway); keel-web: HTTP 200 on 5173.
**Rationale**: no actuator dependency; connection-refused vs any-response is the boot signal.

## 5. Screenshot policy
**Decision**: auto-capture after every browser step (and before destructive clicks), numbered
`NNN-<slug>.png`, full-page; failure additionally saves `page.content()` + console log.
**Rationale**: the bundle is for a human reviewing later (design pass 4); after-only misses
what the founder saw before acting.

## 6. Scenario determinism
**Decision**: scenarios are data-first — payload builders per action + participant answer
table; the driver consults them, never generates; run ids are timestamps taken by the harness
(fine here — not a workflow script).
