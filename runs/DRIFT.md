# Drift and bugs found by S-001

This repo reports bugs in the product repos; it never fixes them (README, design §6). All
findings below were surfaced by running the real stack, not by reading source alone -- each was
reproduced against a live `keel-cloud` + `keel-web` (see the run bundles named beside each).

## 1. Blocking: `GET /v2/projects/{id}/brief` crashes whenever discovery actually succeeds

**Severity: blocking.** This is not an edge case -- it is the successful, intended outcome of a
discovery: a load-bearing assumption that the evidence fully supports.

**Where**: `keel-cloud`
`src/main/java/com/keeldiscovery/cloud/protocol/founder/FounderViewAssembler.java`,
`brief()` (~line 330) and `faithNote()` (lines 349-357).

```java
for (Assumption assumption : project.stage(type).applying()) {
    if (assumption.risk() != Risk.LOAD_BEARING) continue;
    Verdict verdict = project.verdictOf(assumption.id());
    FounderDtos.BriefLine line =
            new FounderDtos.BriefLine(assumption.statement(), faithNote(project, assumption.id(), verdict));
    if (verdict == Verdict.CONTRADICTED) {
        saidNoTo.add(line);
    } else if (verdict != Verdict.SUPPORTED) {
        takingOnFaith.add(line);
    }
}
```

```java
private static String faithNote(Project project, AssumptionId assumptionId, Verdict verdict) {
    ...
    return switch (verdict) {
        case UNTESTED -> "nobody has said anything that counts yet";
        case MIXED -> ...;
        case CONTRADICTED -> ...;
        case SUPPORTED -> throw new IllegalStateException(
                "a SUPPORTED deal-breaker belongs in neither taking-on-faith nor said-no-to");
    };
}
```

`line` (and therefore `faithNote(...)`) is constructed **unconditionally** for every applying
load-bearing assumption, before the `if/else` decides which list (or neither) it belongs on.
`faithNote`'s own switch has no case for `SUPPORTED` other than throwing -- so the very first
load-bearing assumption that the evidence fully supports crashes the whole brief endpoint with an
unhandled `IllegalStateException`, for every stage's brief request that follows.

**Compounding effect**: the unhandled exception triggers Spring Boot's default error-page forward
to `/error`, which is *not* covered by `SecurityConfig`'s `/v2/**` permit-all matcher (only
`/v2/**` and the MCP endpoint are). The forwarded `/error` request falls through to the deny-all
default chain, so the browser sees a bare **403 Forbidden with an empty body** -- not the 500 the
actual failure is. A founder (or an operator reading a network tab) sees only "Request failed with
403" and has no way to tell this apart from an auth problem.

**Reproduction** (either run bundle reproduces this from a fresh project):
```
runs/20260830T022019Z-s001-smoke/
runs/20260830T022100Z-s001-smoke/
```
Both are S-001 runs from independent `make eval K=s001` invocations (T017's required double run)
against a freshly-`make up`'d stack; both fail at the identical step
(`founder opens the brief`) with a fresh project id each time. `failure/page.html` in each bundle
shows the rendered `Request failed with 403` message; `keel-cloud`'s own server log at the time
of either run shows:
```
java.lang.IllegalStateException: a SUPPORTED deal-breaker belongs in neither taking-on-faith nor said-no-to
	at com.keeldiscovery.cloud.protocol.founder.FounderViewAssembler.faithNote(...)
	at com.keeldiscovery.cloud.protocol.founder.FounderViewAssembler.brief(...)
```
Also directly reproducible with curl, bypassing keel-web and the eval harness entirely:
```
curl -s -w '\nHTTP:%{http_code}\n' http://localhost:18080/v2/projects/<id>/brief
# -> (empty body)
# HTTP:403
```

**Why S-001 was not adapted around this**: S-001's participant answers supportively throughout
(design §5's own choice), which is what makes a load-bearing assumption resolve to `SUPPORTED` --
the correct, intended outcome of a discovery that goes well. There is no legitimate alternate path
that reaches a rendering brief screen for a *successful* discovery without either (a) triggering
this bug, by having at least one load-bearing assumption actually get supported, or (b) rigging
the scenario to leave every load-bearing assumption unresolved or contradicted, which would no
longer be testing the scenario design §5 asks for (a discovery that succeeds). S-001 is left as
designed; it fails honestly at this step until the product bug is fixed.

**Not applied, but the shape of the fix**: skip constructing `line`/calling `faithNote` entirely
when `verdict == Verdict.SUPPORTED` (a supported deal-breaker belongs on neither list, which the
surrounding `if/else` already knows -- it just evaluates the line eagerly first). Separately,
`/error` likely needs a route through a chain that can return it (or a `@RestControllerAdvice`
catching `Exception` at the `/v2/**` boundary itself), so an unrelated future bug fails as the 500
it is rather than a misleading 403.

**Update (002-eval-scoring, T018)**: fixed in keel-cloud (`FounderViewAssembler.brief` now skips
`line`/`faithNote` construction on `Verdict.SUPPORTED`, per the shape of the fix above). A live
double-run confirms the brief step no longer 403s: `runs/20260830T032533Z-s001-smoke/` and
`runs/20260830T032606Z-s001-smoke/` both complete through `founder opens the brief` and score the
full run (4.5/5). This finding is resolved; left here for history rather than deleted.

## 2. Non-blocking: `keel_open_web`'s URL contract disagrees with keel-web's actual routes

**Severity: non-blocking** (worked around in the harness; see `harness/browser.py`'s module
docstring for the full write-up). `OpenWebUrls.urlFor` (`keel-cloud`,
`src/main/java/com/keeldiscovery/cloud/protocol/OpenWebUrls.java`, the MCP-only `keel_open_web`
tool's URL builder) disagrees with `keel-web`'s actual routes
(`src/routes/AppRoutes.tsx`) on two of its five screens:

| screen | `OpenWebUrls` builds | keel-web actually serves |
|---|---|---|
| `overview` | `.../{projectId}/overview` | `.../{projectId}` (the index route -- no trailing segment) |
| `stage` | `.../{projectId}/stages/{stage}` | `.../{projectId}/s/{stage}` |
| `invite` | `.../{projectId}/invite` | matches |
| `invitations` | `.../{projectId}/invitations` | matches |
| `brief` | `.../{projectId}/brief` | matches |

Opening either mismatched URL leaves keel-web's inner `<Routes>` (nested under
`/p/:projectId/*`) with nothing to match, so the page renders blank inside `ProjectShell`'s chrome
(no "page not found" -- just an empty content area, which is easy to miss visually).

This driver speaks HTTP, not MCP, so it never actually calls `keel_open_web` -- there is no HTTP
equivalent (design §1's open question 1; the tool is MCP-only, confirmed in its own javadoc). The
harness derives founder screen URLs itself, from the same founder-base-url contract
`OpenWebUrls` uses, as the closest thing to "tool-issued" available over HTTP (see
`harness/browser.py`'s module docstring for the reasoning). That port is what surfaced this
mismatch: it tries the `OpenWebUrls`-shaped URL first, and only falls back to keel-web's actual
route (recording a `DRIFT:` note in the transcript each time) when the first one doesn't render --
which is how S-001 continues past `overview` and `stage` navigations at all. Every S-001 run bundle
carries these two `DRIFT:` notes in its `transcript.jsonl` (`kind: note, party: stack`), e.g.:
```
DRIFT: keel_open_web's 'overview' URL (.../overview) does not match keel-web's actual route; falling back to .../{projectId}
DRIFT: keel_open_web's 'stage' URL (.../stages/PROBLEM) does not match keel-web's actual route; falling back to .../{projectId}/s/PROBLEM
```
**Not applied, but the shape of the fix**: either `OpenWebUrls` should build `stage` as
`/{id}/s/{stage}` and `overview` as `/{id}` (matching keel-web), or keel-web should grow routes
that also accept `/overview` and `/stages/{stage}` (aliasing them to the existing ones) if the
longer paths are the intended public contract instead. Either repo could be "right" here; only the
two must agree.

**Update (002-eval-scoring, T018)**: `OpenWebUrls` now builds `overview` as `/{id}` and `stage`
as `/{id}/s/{stage}` -- matching keel-web, per this class's own updated javadoc, which credits
this repo's finding. `harness/browser.py`'s `_SCREEN_PATHS` was updated to match, and a live
double-run (`runs/20260830T032533Z-s001-smoke/`, `runs/20260830T032606Z-s001-smoke/`) confirms
zero `DRIFT:` notes fire -- the primary URL renders on the first try for every screen now. This
finding is resolved; left here for history rather than deleted.

## 3. Blocking: keel-cloud's own MCP endpoint is unreachable under its shipped default configuration

**RESOLVED 2026-08-30**: keel-cloud now sets `spring.ai.mcp.server.protocol: STREAMABLE` in
application.yml, pinned by `SecurityConfigTest.theMcpEndpointIsMountedWhereSecurityConfigAndTheHostsExpectIt`;
the eval-side env override is removed and the stack gate passes against the shipped config.

**Severity: blocking** -- not on S-001 (this driver speaks HTTP, never MCP), but on the actual
feature the endpoint exists to serve: no real MCP host can reach `keel_open_web` or any other MCP
tool against a freshly-cloned, un-tweaked keel-cloud.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/protocol/SecurityConfig.java`
(the permit-all matcher) and `build.gradle` (`spring-ai-bom:2.0.1`).

```java
// SecurityConfig.java
@Value("${spring.ai.mcp.server.streamable-http.mcp-endpoint:/mcp}") String mcpEndpoint
```

`SecurityConfig`'s own javadoc calls this "the webmvc starter's own property, default `/mcp`" --
true of the *streamable-http* transport, but not of what `spring-ai-bom 2.0.1` (the version
`build.gradle` pins) actually boots by default. Decompiling
`spring-ai-autoconfigure-mcp-server-common-2.0.1.jar`'s
`McpServerAutoConfiguration$EnabledSseServerCondition$SseEnabledCondition` shows:

```java
@ConditionalOnProperty(prefix = "spring.ai.mcp.server", name = "protocol",
                        havingValue = "SSE", matchIfMissing = true)
```

`spring.ai.mcp.server.protocol` defaults to `SSE`, not `STREAMABLE` -- the deprecated
`WebMvcSseServerTransportProvider` mounts instead, at `/sse` (plus a message-post endpoint), a
path `SecurityConfig`'s permit-all list never names.

**Reproduction** (fresh `./gradlew bootRun`, no code changes, from this repo's own `make up`):
```
curl -s -w '\nHTTP:%{http_code}\n' -X POST http://localhost:18080/mcp -d '{}'
# -> {"timestamp":...,"status":404,"error":"Not Found","path":"/mcp"}   HTTP:404
curl -s -w '\nHTTP:%{http_code}\n' http://localhost:18080/sse
# -> HTTP:403 (Forbidden)
```
The 403 on `/sse` versus the bare 404 on `/mcp` is itself the tell: a 403 means Spring Security's
filter chain matched a rule and denied it (so `/sse` *is* a real, registered route, just not
permitted); a 404 means the request was let through by `permitAll` and Spring MVC's dispatcher
found nothing mapped there. So the *actually live* transport is `/sse`, sitting behind the
deny-all default chain -- unreachable by any MCP client using the shipped defaults -- while the
one path `SecurityConfig` bothered to permit was never mounted at all. Both symptoms were
verified against a running stack, not read off the source: `runs/20260830T032325Z-s001-smoke/`
is this repo's own `make up` attempt failing at exactly this gate (`stack/cloud.py`'s
`check_mcp_reachable`, contracts/stack-contract.md) before the workaround below was applied.

**Why S-001 was not blocked by this**: `harness/driver.py`'s docstring already records that this
driver speaks the HTTP agent protocol directly and only ever *touches* `/mcp` once, as a
liveness smoke check -- it never actually calls an MCP tool. So the workaround below unblocks
this repo's own `make up` gate and `harness.driver.check_mcp_reachable`, not S-001's actual test
assertions, which don't depend on MCP at all.

**Worked around, not fixed, in this repo**: `stack/cloud.py`'s `build_env` now sets
`SPRING_AI_MCP_SERVER_PROTOCOL=STREAMABLE` (Spring Boot relaxed env-var binding for
`spring.ai.mcp.server.protocol`) when booting keel-cloud for eval -- a same-binary, environment-
only override, no keel-cloud source touched, that selects the transport `SecurityConfig` was
actually written for. With it, `/mcp` answers `400` on a bodyless POST (a real JSON-RPC/Accept-
header validation error from `WebMvcStreamableServerTransportProvider`, not a routing 404) --
confirming the endpoint is genuinely mounted and reachable once the right transport is selected.
See `stack/cloud.py`'s module docstring for the full reasoning.

**Not applied, but the shape of the fix**: either keel-cloud's `application.yml` should set
`spring.ai.mcp.server.protocol: STREAMABLE` explicitly (matching what `SecurityConfig` already
assumes, rather than relying on a library default that has since changed), or `SecurityConfig`
should permit whichever path(s) `McpServerSseProperties`/the SSE transport actually mounts if SSE
is the intended protocol instead. Either repo-internal choice is fine; the two just have to agree,
the way `OpenWebUrls` and keel-web's routes now do (finding #2, above).

## 4. Non-blocking: the agent's own instructions leak raw protocol vocabulary into what design
   treats as founder-facing text

**Severity: non-blocking** -- discovered by policy v1's CLA-A1 check (contracts/policy-contract.md),
scored low rather than worked around (design §6, FR-008): every S-001 run's `GUIDANCE` and
`CLARITY` categories land at 4.0/5, not 5.0, because of this.

**Where**: `keel-cloud` `keel/v2-instructions.yaml` (loaded by `InstructionRegistry`, served as
`NextResponse.instruction.{purpose,content}` and `.requirements` on every action issuance).

`InstructionRegistry.Instruction`'s own javadoc: *"One line the founder never sees, and one
paragraph the executing client alone reads."* 002-eval-scoring's design (§2, §7 pass 5) treats
exactly this material as the substrate for the report's agent-surface "conversation card" --
"the instruction and requirements as the agent would voice them" -- because there is no real LLM
in this harness to paraphrase it into founder speech first. Read that way, several instructions
leak the model's own vocabulary rather than founder-safe prose:

- `FRAME`'s instruction (I002/I003 in `runs/20260830T032606Z-s001-smoke/`): *"a load-bearing
  belief is **CONTRADICTED**... read the **contradictions** handle... **MIXED** or merely
  **UNTESTED**... reports **SUPPORTED** against a claim nobody is making."* -- four raw `Verdict`
  enum tokens plus a handle name, verbatim.
- `INTRODUCE_ROLES`'s requirements (I004): *"...each with a label, a **roleType**, and an about
  line..."* -- the DTO field name, not a founder phrase for it.
- `INTRODUCE_ASSUMPTIONS`'s requirements (I005, I013, I022): *"**askedOf** naming a role..."* --
  same pattern.
- `INTERPRET`'s instruction (I012, I021, I030): *"Read the **response** handle's raw text..."*
  and requirements naming **perAnswer** entries directly.
- `PROCEED_TO_BRIEF`'s instruction/requirements (I031): *"**goingAhead** exactly when... is
  **CONTRADICTED**"*, *"**openDecisions** for what remains unknown"*, *"read the **brief_inputs**
  handle"*.

**Reproduction**: any S-001 run's `scorecard.json` (e.g. `runs/20260830T032606Z-s001-smoke/`) --
`GUI-A2`/`CLA-A1` fail on interactions I002, I003, I004, I005, I012, I013, I021, I022, I030, I031
naming exactly these tokens, each check's `evidence.steps` pointing at the `get_next` transcript
entry carrying the raw `instruction`/`requirements` strings quoted above.

**Why S-001 was not adapted around this**: the instructions are keel-cloud content
(`v2-instructions.yaml`), not this driver's own text -- there is no legitimate scenario variant
that avoids issuing `FRAME`/`INTRODUCE_ROLES`/`INTRODUCE_ASSUMPTIONS`/`INTERPRET`/
`PROCEED_TO_BRIEF` in a discovery that actually runs the workflow, so every S-001 run will
reproduce this. The check stays strict per policy v1 as shipped (contracts/policy-contract.md's
CLA-A1: "founder-facing text (instruction, requirements, display)... free of raw enums... and
field names") rather than being narrowed to avoid the finding.

**Not applied, but the shape of the fix**: `v2-instructions.yaml`'s prose could describe the same
guidance without the model's own vocabulary (e.g. "when replacing a claim the evidence has ruled
out" instead of naming `CONTRADICTED`; "who can answer, their kind of role, and a neutral one-line
description" instead of naming `roleType`) -- content-only changes, no code. Alternatively, if
this text is genuinely meant to stay implementation-facing (the javadoc's own claim), a future
agent surface would need an explicit paraphrase step before voicing any of it to a founder, which
this no-LLM harness cannot exercise; that boundary is out of scope here (design §6).
