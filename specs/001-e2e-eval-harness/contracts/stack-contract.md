# Contract: Stack Orchestration

## Ports (fixed)
postgres 55432 · keel-cloud 18080 · keel-web 5173. `make up` fails fast, naming the port and
likely owner, if any is taken by a foreign process.

## Env injected into keel-cloud (the load-bearing lines)
```
KEEL_DB_URL=jdbc:postgresql://localhost:55432/keel_cloud
KEEL_DB_USERNAME=keel  KEEL_DB_PASSWORD=keel
KEEL_SERVER_PORT=18080
KEEL_V2_FOUNDER_BASE_URL=http://localhost:5173/p
KEEL_V2_PARTICIPANT_BASE_URL=http://localhost:5173/i
KEEL_V2_FOUNDER_DISPLAY_NAME=Eval Founder
JAVA_HOME=<from stack.toml or environment>
```

## keel-web launch
`npx vite --config <keel-e2e-eval>/stack/vite.eval.config.ts` run in the keel-web checkout;
config sets port 5173 strict + proxy `/v2` → `http://localhost:18080`; api base stays default
(same-origin).

## Health gates
postgres: `docker compose exec pg_isready` · cloud: any HTTP response on 18080 within 120s ·
web: HTTP 200 on 5173 within 60s. `make up` prints each gate as it passes.

## Teardown (`make down`)
killpg recorded pgids (vite, gradle) → wait → `docker compose down -v`. Idempotent; safe when
half-up. `make eval` attaches to a live stack (gates pass fast) or boots one and owns teardown
at session end.

## MCP reachability
One check per stack boot: POST to `http://localhost:18080/mcp` must not be connection-refused/404.
