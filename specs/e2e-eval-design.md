# Keel E2E Eval — Design

**Status**: Proposed. This repository is the *fourth* Keel repo: it owns no product code and
exists to prove the other three (`keel-cloud`, `keel-web`, `keel-skill`) work **together** —
full stack, real browser, real wire — in a way an operator agent can run on demand and a human
can review afterwards from screenshots.

## 1. Purpose and operating model

An operator agent (or a person) clones this repo beside the other three and runs:

```bash
make up        # docker Postgres + keel-cloud + keel-web, health-gated
make eval      # run every scenario;   make eval K=s001  runs one
make down      # tear the stack down
```

Each scenario plays **all three parties of a discovery**: the founder's AI agent on the wire,
the founder in the browser, and the stranger answering the survey in a second browser context.
Every run leaves an evidence bundle a human reviews later — that bundle, not the green
checkmark, is the product of a run.

## 2. Topology (verified against the repos, not assumed)

| Piece | How | Port | Source of truth checked |
|---|---|---|---|
| Postgres 16 | `docker-compose.yml` in this repo | **55432** (never 5432 — Colima/testcontainers own that neighborhood) | keel-cloud `application.yml` reads `KEEL_DB_URL` |
| keel-cloud | `./gradlew bootRun` in the sibling checkout, env-injected | **18080** | `KEEL_SERVER_PORT`; Flyway migrates on boot; `/v2/**` + `/mcp` are permit-all (auth deferred, gate 8) |
| keel-web | `npx vite` with an **eval-owned config** (see §4 pass 2) | **5173** | routes `/p/:projectId/*` (founder) and `/i/:token` (participant); API base via `VITE_KEEL_CLOUD_API_BASE`, default same-origin |
| SKILL.md | read from the sibling `keel-skill` checkout | — | the founder-agent driver derives its conduct from it |

Environment injected into keel-cloud — and these two lines are load-bearing:

```
KEEL_V2_FOUNDER_BASE_URL=http://localhost:5173/p
KEEL_V2_PARTICIPANT_BASE_URL=http://localhost:5173/i
```

because the shipped **defaults point at `localhost:3000/projects`, a URL keel-web does not
serve** (it serves `/p`). That mismatch — found while writing this design — is exactly the class
of cross-repo drift no single repo's test suite can see, and it becomes a standing assertion:
every URL a tool hands out must actually render in the browser that opens it (never construct
URLs in the eval; open what the tool returned).

Sibling paths live in `stack.toml` (defaults `../keel-cloud` etc.). Every run records
`versions.json`: the git commit of all four repos at run time.

## 3. The three parties

**FounderAgent** — a Python protocol driver in this repo. It loads SKILL.md and runs the loop
(`get_next` → branch on `kind` → `get_context` → submit) against the real server over the HTTP
agent surface (`/v2/agent/**`), which keel-cloud parity-tests against the MCP binding; one
reachability check touches `/mcp` itself so a dead MCP endpoint still fails a run. **No LLM
anywhere**: the founder's half of the conversation comes from the scenario script — each
scenario supplies deterministic payload builders per issuance (opportunity statements, role
lists, assumption sets, interpretations), so runs are reproducible and diffable.

**FounderBrowser** — Playwright (chromium). Executes precisely what handoffs delegate:
`REVIEW` → open the URL `keel_open_web` returned, read the stage, click approve;
`INVITE` → open the invite screen, type the about-line, mint the link, *copy the link the UI
shows* (that string is what the participant gets — again, never constructed); plus the final
brief reading. Screenshots at every step.

**Participant** — a second, isolated Playwright browser context (a stranger shares no session
with the founder). Opens `/i/:token`, screenshots the consent framing and every question,
answers per the scenario's answer table (support / contradict / skip per assumption), submits,
screenshots the thank-you. `WAITING` handoffs resolve because this party acts — the eval
choreographs the same interleaving a real discovery has.

## 4. The eval framework

`pytest` + Playwright (sync API). One session-scoped `stack` fixture (attach if `make up` is
already live, else boot and own the teardown); one function-scoped `run_dir`.

**Step API**: `with step("participant answers the pricing question"):` — every step appends a
`transcript.jsonl` entry; browser steps auto-capture numbered screenshots (`023-participant-
pricing.png`); protocol steps record the full request/response pair. On failure the step
additionally dumps page HTML and browser console.

**Evidence bundle** per run: `runs/<timestamp>-<scenario>/` containing `transcript.jsonl`,
`screenshots/`, `versions.json`, `verdict.json`, and a generated `report.html` — step list with
inline thumbnails, protocol excerpts, and the verdict — the artifact the user actually reviews.

**Isolation**: a fresh project per scenario (projects are the aggregate boundary; cheap and
sufficient); the database resets only at `make up`.

## 5. Scenarios

Implemented now: **S-001, the smoke** — create → frame PROBLEM → roles → assumptions → REVIEW
handoff → founder approves in browser → (×3 stages) → INVITE → about-line typed → participant
opens link, consents, answers supportively, submits → WAITING resolves → INTERPRET (issuance
names the invitation; driver reads `response`) → verdicts move on the overview → brief. It
exercises every party, every handoff reason, every screen, and the URL contract.

Deliberately **not** designed here: the positive/negative catalog (contradicted load-bearing
warning, reframe-stale link, concurrency, all-skipped submission, unknown screen…). The user
picks those together with us once the harness stands; the framework just makes each one a
scenario module with payload builders + answer tables + assertions.

## 6. Non-goals

No LLM calls in evals; no cloud CI (local-first; CI can come later); no auth testing (deferred
with keel-cloud gate 8); no load/perf testing; no product code — this repo must never grow a
fix that belongs in one of the other three (finding drift and *reporting* it is its job).

## 7. Five passes

1. **Config-truth pass**: read `application.yml`, `SecurityConfig`, `vite.config.ts`,
   `AppRoutes.tsx` instead of trusting memory — caught the `/projects`-vs-`/p` base-URL
   mismatch and turned it into both a required env override and a standing assertion (§2).
2. **Network-reality pass**: keel-cloud has no CORS configuration, so a browser on 5173
   fetching 18080 cross-origin fails — resolved with an **eval-owned vite config** that proxies
   `/v2` to keel-cloud, leaving both product repos untouched; keel-web's api base stays
   same-origin, exactly as deployed.
3. **Determinism pass**: no LLM, scripted founder; dedicated ports (55432/18080/5173) so a
   developer's own Postgres or dev server never collides; `versions.json` pins all four repos
   so a reviewed run is reproducible.
4. **Evidence-quality pass**: a screenshot nobody can find is worthless — numbered files keyed
   to transcript steps, an HTML report with thumbnails, failure dumps with page HTML and
   console; the report is generated even when the scenario fails (especially then).
5. **Lifecycle pass**: `bootRun` cold-starts in 30–60s — health gates poll a real endpoint
   (`GET /v2/...` returning anything but connection-refused) with a generous budget; children
   spawn in their own process groups so `make down` reliably kills gradle's tree; `make eval`
   against an already-up stack is the fast iteration path.

## 8. Open decisions

1. HTTP agent surface vs MCP as the driver transport — **HTTP**, with an `/mcp` reachability
   check; the parity suite in keel-cloud carries the equivalence. Revisit if a Python MCP
   client becomes worth the dependency.
2. Whether `report.html` should aggregate across runs — deferred; per-run reports first.
