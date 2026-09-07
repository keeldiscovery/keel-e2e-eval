# Drift and bugs found by the eval set

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

## Re-adjudication, 2026-08-30 (003-eval-set, policy v2)

**Finding #4 above is reclassified: policy category error, not a product text bug.** Nothing in
`keel-cloud` changed to produce this; the eval's own policy was measuring the wrong surface.

Re-reading the shipped contract before writing any more checks on top of it (003-eval-set design
§2, plan.md's adjudication pass) found that `v2-instructions.yaml`'s `instruction.content` and
`ActionSchemas.requirements` are not founder-facing text at all — they are the agent's own
methodology and payload guidance, exactly as `InstructionRegistry`'s javadoc already said ("one
line the founder never sees, and one paragraph the executing client alone reads") and as
`ActionSchemas.requirements` itself demonstrates by naming `CONTRADICTED`/`askedOf`/`goingAhead`
in its own shipped, correct copy — vocabulary a schema-and-methodology guide legitimately uses and
a founder never reads raw. Policy v1's CLA-A1/GUI-A2 checks swept both texts with the same
founder-language yardstick as a handoff's `display`, which is the one protocol text actually
relayed to a founder. That was the eval's mismeasurement, not keel-cloud's leak.

**What did not change**: the UI sweeps (`CLA-U1`/`CLA-U2` on every rendered founder/participant
page) and the participant-page sweep stayed at full strength throughout — they are what would
catch a real founder-facing leak, and finding #4 was never about them. A handoff's `display` also
stays swept (`CLA-A1`, and now also `GUI-A2`, policy v2) — it is the one protocol text a founder
does receive, and a seeded raw enum there still fails both checks (`tests/test_policy_v2.py`).

**Action taken**: `evals/policy.py` POLICY_VERSION → 2; `CLA-A1`/`GUI-A2` no longer apply to
agent-cycle interactions (`instruction`/`requirements`) at all; `GUI-A2` gains a handoff variant
sweeping `display`, alongside the existing handoff `CLA-A1`. `GUI-A1`'s presence/sentence-shape
check on `requirements` and `ORI-A1`'s presence check on `instruction.content` are untouched —
neither ever vocabulary-swept. `specs/eval-scoring-design.md` §3 carries the dated amendment.

**Live proof**: re-scoring the existing S-001 bundle (`runs/20260830T033544Z-s001-smoke/`, no
rerun against the stack needed — `make report RUN=<dir>` re-derives interactions and re-scores
from `transcript.jsonl` + `facts.json` alone) under policy v2:

| | policy v1 (before) | policy v2 (after) |
|---|---|---|
| GUIDANCE | 4.0/5 | 5.0/5 |
| CLARITY | 4.0/5 | 5.0/5 |
| ORIENTATION | 5.0/5 | 5.0/5 |
| FIDELITY | 5.0/5 | 5.0/5 |
| run score | 4.5/5 | 5.0/5 |
| failing checks | 20 (`GUI-A2`×10, `CLA-A1`×10, all on `FRAME`/`INTRODUCE_ROLES`/`INTRODUCE_ASSUMPTIONS`/`INTERPRET`/`PROCEED_TO_BRIEF` agent-cycle issuances) | 0 |

All twenty v1 failures disappear because the checks that raised them no longer apply to that
interaction type — not because anything about `v2-instructions.yaml` or `ActionSchemas` changed.
This finding is resolved as a policy fix; left here (not deleted) for the same reason findings #1–3
above are kept after their product fixes: the history of what was wrong and why is the record.

## 5. Blocking: a carrying `FRAME` reframe can never gain a new assumption -- the replaced belief simply vanishes

**Severity: blocking.** journeys.md §1.9's central promise about a pivot -- "New things to be true
appear under the new claim, all unanswered... nobody is asked a question the evidence has already
settled" -- is only half true. The old belief really is superseded and a survivor really is
carried; but no *new* belief can ever be introduced in the same review cycle a carrying reframe
opens, through the shipped agent protocol, no matter what the founder and their agent discuss.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/protocol/NextRecommendation.java`,
`reviewRecommendation` (~line 104):
```java
private static Recommendation reviewRecommendation(Project project, StageType stage) {
    if (!project.stage(stage).applying().isEmpty()) {
        return new HandoffRec("REVIEW", "... waiting for your approval ...", ...);
    }
    return project.roles().isEmpty() ? INTRODUCE_ROLES : INTRODUCE_ASSUMPTIONS;
}
```
This is only ever reached while a stage is framed and unapproved. It recommends decomposing
(`INTRODUCE_ROLES`/`INTRODUCE_ASSUMPTIONS`) exactly when `applying()` is empty -- true for a
stage's first-ever framing, but **false** the instant a reframe carries even one survivor forward
(`Project.frame`'s whole point: a carried assumption keeps `stillApplies() == true`). So the very
next `get_next` after a carrying `FRAME` is a `REVIEW` handoff, never `INTRODUCE_ASSUMPTIONS` --
and because a token is only ever minted for the action `get_next` itself just recommended
(`AgentProtocolService.issue`/`submit` -- there is no "give me a token for a different action"
call), **the agent has no protocol-legal way to introduce a new pricing question in this cycle**.
Approving the stage with only the carried survivor goes straight to `PROCEED_TO_BRIEF`
("recommended once nothing is left to settle") -- the replaced deal-breaker is not replaced with
anything; it is simply gone, forever, unless some *later* reframe reopens the stage again.

**Reproduction** (live, reproduced by every run of `test_s002_pricing_pivot.py`, e.g.
`runs/20260830T043949Z-s002-pricing-pivot/`): drive a project to "commercial pricing ruled out,
budget-owner supported" (`evals/recipes.rule_out_pricing`), submit the offered `FRAME` reframe
carrying only the budget-owner assumption, then call `get_next` again:
```
{"kind": "handoff", "reason": "REVIEW", "display": "The commercial card is waiting for your
 approval -- read the questions before anyone is asked.", "detail": {"stage": "COMMERCIAL"}}
```
Approve that stage (with only the carried belief) and call `get_next` once more:
```
{"kind": "action", "action": "PROCEED_TO_BRIEF", ...,
 "detail": {"note": "recommended once nothing is left to settle; this is the founder's call, ..."}}
```
No `INTRODUCE_ASSUMPTIONS` ever appeared. `evals/recipes.py`'s module docstring carries the full
derivation; `test_s002_pricing_pivot.py` asserts this exact sequence every run rather than reaching
for a workaround (design §6) -- if a future fix makes `INTRODUCE_ASSUMPTIONS` reachable here, that
test takes the win automatically (its assertion branches on the discovery, it does not require the
gap to persist).

**Why S-002 was not adapted around this**: there is no legitimate alternate path -- carrying
*anything* forward reproduces it, and carrying *nothing* forward would lose the survivor's
evidence entirely (the other half of design §3's requirement). The scenario walks the reframe
exactly as the product allows and documents where it falls short of the journey, per design's
discovery-honesty pass, rather than silently arranging for the gap never to be exercised.

**Not applied, but the shape of the fix**: `NextRecommendation.reviewRecommendation` (or
`Project.needs`) needs a way to distinguish "this stage has never been decomposed" from "this
stage was just reframed and may still want new beliefs alongside its carried survivor" -- e.g. a
flag on the frame itself (mid-reframe vs. steady-state), or recommending `INTRODUCE_ASSUMPTIONS`
whenever the *active frame* has never had an assumption introduced against it specifically, rather
than keying off the stage's `applying()` list as a whole.

**RESOLVED, 2026-08-30 (keel-cloud commit `c63ad4a`)**: fixed exactly along the shape of the fix
above. `Stage.decomposedForActiveFrame()` (new) distinguishes "the active frame has a belief
introduced against it specifically" (its `introducedAt` not before the active frame's own
`framedAt`) from "the active frame only inherited a carried survivor" (whose `introducedAt` stays
that of the earlier frame, strictly before the new one's); `NextRecommendation.reviewRecommendation`
now keys off that instead of `applying().isEmpty()`. Design amendment recorded in
`action-protocol-design-r2.md` §8a (dated 2026-08-30, credits this finding by name).

Live proof: `test_s002_pricing_pivot.py` (upgraded the same day) now walks the real cycle the
reproduction above showed was missing -- the `get_next` immediately after a carrying `FRAME` is
`INTRODUCE_ASSUMPTIONS`, not the `REVIEW` handoff this finding documented; the new pricing belief
it introduces (`NEW_COMMERCIAL_PRICING_ASSUMPTION`, under the new per-run claim) arrives unapproved
and the stage reopens for `REVIEW` with both the new belief and the carried survivor on it; the
carried budget belief's verdict (`SUPPORTED`) and applying status survive the whole cycle untouched
(asserted directly against the `opportunity` handle); and a fresh invitation minted afterward for
the new belief carries only that one question -- `Stage.linkFor` never re-freezes budget, since it
is already `SUPPORTED` (not `Verdict.isOpen()`) regardless of role assignment. This finding is
resolved; left here for history rather than deleted.

## 6. Non-blocking: a never-opened invitation can leave a founder's workflow waiting forever on a link the participant is told is already dead

**Severity: non-blocking** (narrow: only bites a link that (a) asks about more than one belief,
(b) is never opened, and (c) survives a reframe that carries at least one of those beliefs
forward) -- but a real, confirmed inconsistency between what the founder's side of the protocol
believes and what the participant is told.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/domain/project/Project.java`,
`needs()`'s `anyPending` check, versus
`src/main/java/com/keeldiscovery/cloud/protocol/participant/ParticipantController.java`'s
`stale()`.

`ParticipantController.stale()` marks a link stale the instant **any one** of the assumptions it
asked about no longer applies:
```java
private static boolean stale(Project project, Invitation invitation) {
    return invitation.asks().stream().anyMatch(id -> project.assumptionOf(id).map(a -> !a.stillApplies()).orElse(true));
}
```
But `Project.needs(stage)`'s `anyPending` check still counts that same unanswered invitation as
something the founder is waiting on, as long as **any** of its `asks` still applies:
```java
boolean anyPending = invitations.stream()
        .filter(inv -> applying.stream().anyMatch(a -> inv.asks(a.id())))
        .anyMatch(inv -> !inv.isAnswered() || !inv.isRead());
```
A link asking about two beliefs, one of which gets superseded by a reframe and one of which is
carried forward, is therefore **stale to the participant** (don't bother -- one of the questions
died) while **still pending to the founder's workflow** (`needs()` returns `ANSWERS`, not
`EVIDENCE` or done) -- `Project.needs` never resolves that stage until the participant answers a
link they were explicitly told not to bother with, or the founder starts an entirely new reframe.

**Reproduction**: found while building `evals/recipes.py`'s `rule_out_pricing` (see that module's
docstring) -- inviting one respondent to a single role covering both the commercial stage's
budget-owner and pricing beliefs, leaving them unanswered, then reframing (carrying budget-owner)
reproduces `get_next` returning `{"reason": "WAITING", "display": "Answers are still out for the
commercial card..."}` forever afterward, even though `GET /v2/i/{token}` for that same invitation
already answers 410 with "This link has gone stale". `evals/test_s002_pricing_pivot.py` avoids
exercising this on its own critical path by asking budget-owner and pricing of two separate roles
instead (a scenario-side design choice, not a product fix) -- see that module's own docstring for
why.

**Not applied, but the shape of the fix**: `anyPending` (or `Invitation`/`Project` more broadly)
could be taught the same per-invitation staleness `ParticipantController.stale()` already computes
-- excluding a link from "pending" once every belief it could still contribute to no longer
applies, or once *any* of its questions is dead, whichever product intends. Either repo-internal
choice is fine; the two just have to agree, the way `OpenWebUrls` and keel-web's routes now do
(finding #2).

**RESOLVED, 2026-08-30 (keel-cloud commit `c63ad4a`)**: fixed exactly along the shape of the fix
above. `Project.isInvitationStale(Invitation)` (new) is the single derivation both sides now read:
an invitation is stale the instant any one of its frozen `asks` no longer applies (verbatim the
predicate `ParticipantController.stale()` used to compute locally, now delegating to this method).
`needs()`'s `anyPending` check was rewritten to match: an already-answered invitation still counts
as pending until read (nobody's submitted work is silently dropped), but an *unanswered* one counts
as pending only while it is not stale -- once every belief it asked about has been superseded,
there is nothing left to wait for. Design amendment recorded in `action-protocol-design-r2.md` §8a
(dated 2026-08-30, credits this finding by name).

**Caveat on the live proof**: this scenario's own two-role split (recipes.py's judgement call,
recorded in the reproduction above) means neither test in this eval set constructs the exact
mixed-ask invitation (one link spanning both a carried survivor and a soon-superseded belief) this
finding's reproduction used -- that would require restructuring which role each commercial belief
is asked of before either resolves, a change to the scenario's own critical path this upgrade
deliberately left alone (see `test_s002_pricing_pivot.py`'s `assumptions_payload` docstring for the
full reasoning). What *is* verified live, in `test_s002_pricing_pivot.py`: the never-opened
pre-pivot pricing link (single-ask, superseded by the reframe) still renders the correct
out-of-date notice to the participant (`ParticipantController.stale()`, reading the same
`isInvitationStale` this fix introduced), and `Project.needs`/`get_next` never wedges on `ANSWERS`
because of it, all the way through to a fresh invitation for the new pricing belief actually being
reachable. The fix is code-level unification (one method, two callers) rather than a
scenario-specific behavior change, so this is taken as sufficient confirmation; the precise
mixed-ask shape remains undemonstrated by this eval set and is noted here rather than silently
assumed. This finding is resolved; left here for history rather than deleted.

## 7. BLOCKING (the eval set's most significant finding): `PROCEED_TO_BRIEF` is unreachable through the shipped agent protocol whenever a load-bearing deal-breaker sits contradicted on an approved, unreframed stage

**Severity: blocking.** journeys.md §1.10's entire "going ahead anyway" conversation -- the
founder asks for the brief despite a disproved deal-breaker; Keel warns and offers a choice;
if the founder goes ahead, the brief renders a GOING AHEAD ANYWAY box with their own sentence --
has **no protocol-legal entry point**. `Project.proceedToBrief`'s A9 business rule (require
`goingAhead` exactly when a load-bearing assumption is `CONTRADICTED`) is correct and unit-tested
in isolation, but no real agent or MCP client speaking only the shipped `get_next`/`submit`
protocol can ever reach a `PROCEED_TO_BRIEF` token in the state A9 exists to police.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/protocol/NextRecommendation.java`
(`compute`, `~line 65`) and `src/main/java/com/keeldiscovery/cloud/domain/project/Project.java`
(`currentFocus`, `~line 526`; `needs`, `~line 495`).

```java
// NextRecommendation.compute
Optional<Focus> focus = project.currentFocus();
if (focus.isEmpty()) {
    return new ActionRec(AgentAction.PROCEED_TO_BRIEF, ...);   // the ONLY way this is ever recommended
}
```
```java
// Project.currentFocus
for (StageType type : StageType.values()) {
    if (needs(type).orElse(null) == Need.REFRAME) {
        return Optional.of(new Focus(type, Need.REFRAME));      // absolute priority, wins outright
    }
}
```
```java
// Project.needs
boolean anyContradictedLoadBearing = ...;
if (anyContradictedLoadBearing) {
    return Optional.of(Need.REFRAME);                            // checked before ANYTHING else
}
```
A load-bearing `CONTRADICTED` assumption can only exist on an *approved* stage (only approved
stages ever collect evidence), so this branch is reachable the moment one appears, and stays
reachable -- `currentFocus()` can never be empty -- until that stage is reframed. Since a token is
minted only for the action `get_next` itself just recommended
(`AgentProtocolService.issue`/`submit`; there is no call that mints a token for a different
action), **there is no way for a real client to ever submit `PROCEED_TO_BRIEF` in this state.**
Not "refused with A9" -- genuinely never offered a token to attempt it with.

**Reproduction** (live, reproduced by every run of `test_s003_going_ahead.py`, e.g.
`runs/20260830T044347Z-s003-going-ahead/`): drive a project to "commercial pricing ruled out,
budget-owner supported, commercial stage still approved and unreframed"
(`evals/recipes.rule_out_pricing`, no reframe submitted), then call `get_next` three separate
times:
```
{"kind": "action", "action": "FRAME", "detail": {"stage": "COMMERCIAL", "reason": "REFRAME"}, ...}
{"kind": "action", "action": "FRAME", "detail": {"stage": "COMMERCIAL", "reason": "REFRAME"}, ...}
{"kind": "action", "action": "FRAME", "detail": {"stage": "COMMERCIAL", "reason": "REFRAME"}, ...}
```
Every call, forever, until reframed. `PROCEED_TO_BRIEF` never appears.

**Corroborating evidence, from keel-cloud's own test suite**: `AgentProtocolFlowTest`
(`src/test/java/com/keeldiscovery/cloud/protocol/AgentProtocolFlowTest.java`) is the one test that
exercises A9's refusal-then-accept behaviour end to end -- and it does so only by minting the
`PROCEED_TO_BRIEF` token directly, bypassing `get_next` entirely:
```java
String briefTokenNoGoingAhead = mintDirect(AgentAction.PROCEED_TO_BRIEF, projectId,
        beforeBriefAttempt.revision());
```
`mintDirect` is a test-support helper (also used mid-flow for `INTRODUCE_ASSUMPTIONS` in the same
test) with no HTTP or MCP equivalent -- not a path any real agent has. This is not proof the gap
was known and accepted; if anything it suggests the test was written by driving the aggregate
directly rather than by simulating a client that only ever acts on `get_next`'s own
recommendation, which is exactly the discrepancy this eval set's driver design (FR-003: "no LLM,
consult only context, never generate a token you weren't issued") was built to catch.

**Why S-003 was not adapted around this**: there is no legitimate alternate path -- any sequence
of agent-only actions that leaves a load-bearing belief contradicted on an approved stage
reproduces this, by construction of `needs()`/`currentFocus()`. `test_s003_going_ahead.py` builds
exactly the state the journey opens from, demonstrates the block with three separate `get_next`
calls (so a transient blip cannot be mistaken for the finding), and stops -- its own `passed` flag
is `False` and its score is honestly gated at 2.0/5 by the completion gate, rather than the test
quietly substituting S-002's pivot flow or fabricating a refusal that was never actually offered.

**Not applied, but the shape of the fix**: `NextRecommendation.compute` needs a way to recommend
`PROCEED_TO_BRIEF` as *available* (not mandatory) even while a `REFRAME` need exists elsewhere --
e.g. only forcing `REFRAME` priority once the founder has been offered and declined the brief, or
exposing a `founder wants the brief now` signal `get_next` can consult that overrides the default
recommendation for one call. Either way, A9's own rule needs no change; it is `currentFocus()`'s
unconditional `REFRAME` priority that forecloses the conversation A9 was written to police.

**RESOLVED, 2026-08-30 (keel-cloud commit `c63ad4a`)**: fixed exactly along the "exposing a
`founder wants the brief now` signal" shape of the fix above. `get_next` now accepts an optional
`request` parameter admitting exactly one value, `"brief"` (`AgentProtocolController`/`KeelMcpTools`
on both transports, `NextRecommendation.founderRequestedRecommendation`): present, it issues
`PROCEED_TO_BRIEF` outright regardless of `currentFocus()`, refusing `"legality"` only if some
stage has never been framed (there is nothing to brief about a claim nobody has stated), and
`"schema"` for any value other than `"brief"`. `A9` itself needed no change -- the refusal it was
always meant to run now finally has a token to run against. Design amendment recorded in
`action-protocol-design-r2.md` §8a (dated 2026-08-30, credits this finding by name as the eval
set's most significant).

**The `AgentProtocolFlowTest` `mintDirect` bypass this finding's corroborating evidence pointed at
is retired for this scenario**: keel-cloud's commit message for `c63ad4a` records that the flow
test's `mintDirect` shortcut for `PROCEED_TO_BRIEF` was replaced with a real `request=brief`
`get_next` call, closing the exact gap between "the domain rule is unit-tested" and "a real client
can reach it" this finding raised.

**Live proof**: `test_s003_going_ahead.py` (rewritten the same day, replacing the old
"three-calls-prove-the-block" design with the real walk) now drives the actual journeys.md §1.10
conversation end to end against the live stack: `driver.get_next(request="brief")` returns
`PROCEED_TO_BRIEF` while pricing still sits `CONTRADICTED` and unreframed; a first submission
omitting `goingAhead` is refused with rule `A9` and a remedy asserted to be sentence-shaped and to
actually name what to do (write the sentence, set `goingAhead`); the identical token -- not a
freshly minted one, confirming the not-consumed-on-refusal contract holds for a domain refusal, not
just a schema one -- is resubmitted with the founder's own sentence and the project reaches
`READY_TO_BUILD`; the rendered brief shows the GOING AHEAD ANYWAY box as the brief's first child,
containing the founder's sentence verbatim, with the disproved pricing belief filed only under
"what the evidence said no to" and never under "taking on faith". This finding is resolved; left
here for history rather than deleted.

## 8. BLOCKING (shaping gauntlet, Layer 2): the keel-discovery skill is never invoked from a founder's cold opening line, so the CREATE/FRAME/INTRODUCE_ASSUMPTIONS shaping mandates under test never run at all

**Severity: blocking.** This is not "the shaping instructions probed weakly" -- it is one level
more fundamental: the real agent (the locally installed `claude` CLI, headless, loaded with the
actual `keel-skill` SKILL.md and the real MCP stack -- `specs/shaping-eval-design.md`'s own
"playground's shape, automated") never touched the Keel protocol at all across a full 12-turn,
three-topic (problem/solution/commercial) conversation. `keel_get_next` was never called, so
CREATE's quantifiability probe, FRAME's mechanism-in-a-sentence test, and
INTRODUCE_ASSUMPTIONS' normalization pass -- the entire feature this gauntlet exists to prove --
never got a chance to run.

**Where**: `keel-skill/SKILL.md`, the frontmatter `description`:

```yaml
description: >-
  Reference interpreter for the keel agent protocol r2, over MCP. Teaches a host
  AI the five stable Keel tools and the keel_get_next -> branch on kind ->
  keel_get_context -> reason with the founder -> keel_submit_action ->
  keel_get_next loop, including handoff conduct and the interpret loop. Keel
  Cloud owns authoritative workflow state; this document teaches only how to
  interpret the protocol, never what any Keel action means.
```

This description is written entirely as *protocol mechanics for a host that has already decided
to use it* -- there is no clause a skill-relevance matcher could key off of to recognize "a
founder describing a business problem" as a trigger. Combined with the gauntlet's own deployment
shape (design's explicit contract: "the agent process gets ONLY what a real host gets" -- SKILL.md
+ the MCP tools + the founder's words, nothing else: no system prompt, no CLAUDE.md, no explicit
skill invocation), a bare `claude -p "<founder's opening line>"` session has nothing else in its
context that would make it reach for this skill on a cold first turn.

**Reproduction** (live, `runs/20260831T022954Z-shaping-gauntlet/`): `make eval-shaping`'s one real
run. Turn 1's founder line was the literal vague opener design §1 specifies, `"Restaurants
struggle with inventory."` The agent's raw `claude -p` response (`transcript.jsonl` seq 4) shows
`"num_turns": 1` -- a single-shot text reply, zero tool calls of any kind:

```
FOUNDER: Restaurants struggle with inventory.
AGENT  : That's true — but it's a pretty broad statement. What's the actual task here? A few
         ways I could help: - Build/improve an inventory tracking app or feature ...
```

The conversation continued for 12 turns touching problem, solution ("I'll build an app for it")
and commercial ("I guess people would pay for it") -- the agent used ordinary general-purpose
tools twice (`num_turns: 4` at turns 6 and 11 -- writing and opening a standalone
`inventory.html` prototype, then a web search for competitor pricing) but **never once** a
`keel_*` tool. `shaping_scorecard.json`'s own `project_id: null` and `"earned": {"price": 7}` (the
agent only ever incidentally asked about price, in the ordinary course of a generic product
conversation, never as part of any Keel-shaped decomposition) confirm no project was ever created
on the stack.

Two follow-up diagnostic calls (same stack, same agent key, same `.mcp.json`/SKILL.md setup,
outside the scored run -- confirming *why*, not re-running the gauntlet) rule out an MCP wiring
problem and pin the cause precisely on skill *triggering*, not connectivity or skill *awareness*:

1. Asked directly, cold, in a fresh session: `"List the exact names of every MCP tool you
   currently have access to"` -> the model correctly lists all five (`mcp__keel__keel_get_context`,
   `keel_get_next`, `keel_get_state`, `keel_open_web`, `keel_submit_action`). MCP is connected and
   the tools are visible.
2. Asked, cold, in a fresh session: `"What skills do you currently have loaded"` -> the model
   correctly names `keel-discovery` among its list. Then, asked *explicitly* whether it would
   consult `keel-discovery`/the MCP tools before replying to the exact same opening line
   (`"Restaurants struggle with inventory."`), the model answers: *"Yes. That statement reads as
   a founder's problem-space input, which is exactly what the keel-discovery skill and its MCP
   tools ... are built to handle ... Before replying, I'd invoke keel-discovery."*

So the model, reflectively, agrees the skill is exactly right for that line -- it simply never
reaches for it proactively on a genuinely cold first turn in this deployment shape. This is a
skill-*activation* gap, not a missing tool, a broken MCP config, or a model that doesn't know the
skill exists.

**Why this scenario was not adapted around**: there is no legitimate alternate path that stays
honest to what this eval is for. Design §2's own contamination/boundary pass is explicit: "the
agent process gets ONLY what a real host gets" -- adding a system prompt, a CLAUDE.md nudge, or an
explicit first-turn skill invocation to make the agent reach for `keel-discovery` would be curing
the exact gap this run exists to surface, the same category of temptation the design names for the
founder-simulator side ("never tune the simulator to make a failure go away"). The gauntlet ran
exactly once, as instructed, against the real CLI with no such scaffolding added; SHP-1 (problem
quantified), SHP-3 (solution mechanism) and SHP-4 (commercial honesty) all fail honestly because
there is no recorded stack to check at all -- `harness/shaping_scoring.py`'s `empty_stage`
fallback, not a harness crash. SHP-2/5/6/7 pass, but vacuously (nothing was ever said on the wire
to be faked, vague, duplicated, or unsurfaced) -- the SHAPING score of 3.0/5 should be read as "3
checks never had anything to fail on," not "the methodology mostly held."

**Not applied, but the shape of a fix**: this is `keel-skill`'s to fix, not `keel-cloud`'s --
`v2-instructions.yaml`'s CREATE/FRAME/INTRODUCE_ASSUMPTIONS content was never reached, so this run
says nothing about whether that content itself is strong enough (Layer 1 already proves it's
*delivered*; Layer 2 needs a real conversation to reach it before it can prove *efficacy*). Two
candidate directions, neither applied here: (a) broaden `SKILL.md`'s frontmatter `description` to
include trigger language a skill-relevance matcher can key off of ("Use when a user describes a
business problem, idea, or something they want to validate" -- not just "reference interpreter for
the protocol"); or (b) if `keel-web`'s real production deployment supplies additional bootstrap
context this harness's bare `claude -p` intentionally does not (a system prompt, an explicit first
invocation) to get a real founder session into the protocol reliably, that gap between "what
`keel-skill` alone provides" and "what a founder session actually needs" is itself worth naming
explicitly rather than left implicit in `keel-web`'s own wiring.

## 9. Methodology (keel-cloud instructions): the agent composed a mechanism the founder never gave

**Found by**: shaping gauntlet run `20260831T091912Z` (SHP-3 + SHP-7, both firing correctly).
The simulator held the mechanism hostage; the agent never asked, and instead of recording the
unknown it wrote a plausible mechanism of its own into the solution claim ("enters count into
the app; automatically compares; flags discrepancies") — a hypothesis nobody holds. Run
`20260831T091346Z` shows the other path (probe asked, mechanism earned), so the instruction
permitted both.

**RESOLVED 2026-08-31**: v2-instructions.yaml FRAME content sharpened — the mechanism must be
the founder's own account: ask, or record the named unknown; never compose one on their behalf.

## 11. Product gap (found by the founder's first real relay use): no shipped host bridge

The relay design's "the poll is the host's mechanical loop" was implemented in the eval harness
and taught in SKILL.md 2.5.0 — but no runnable bridge shipped for a real founder's machine, so
the playground's chat honestly reported the agent disconnected: nothing existed to connect it.
Second, smaller hole behind it: the relay (and the chat rail) are per-project, so a founder's
very first conversation — the one that creates the project — still has no home in the browser.

**Stopgap 2026-08-31**: keel-playground/bridge.py — the gauntlet's proven claude-CLI loop as a
standalone script (long-poll → wake claude per founder turn → post reply; lease honored,
mechanical poll). Productization open: a first-class bridge artifact (where it lives is a design
question — host tooling, not the Markdown-only skill), and a project-less lobby chat for the
first conversation.

## 12. Harness hygiene: the isolation test left its account in the playground volume

The split-stack live verification provisioned a synthetic founder account on the playground
profile and tore down the containers but not the named volume — so the founder's real first-run
setup was refused by a squatter. Fixed operationally (volume wiped); rule for the harness: any
test touching the playground profile must remove its volume on teardown, or better, never
provision on the playground profile at all — verify isolation by ports/containers alone.

## 13. Non-blocking: the guided walk's own step-scoped exchange can never show an agent's reply

**Found by**: S-001's guided-walk re-choreography (run `runs/20260831T234713Z-s001-smoke/`),
reading keel-cloud d408dbf and keel-web 96c83af together.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/application/RelayService.java`,
`appendAgentTurn` (the private helper `postAgentTurns` calls) -- every agent-posted turn is stored
with `step` hardcoded to `null`:
```java
RelayTurn stored = repository.append(
        RelayTurn.draft(id, Author.AGENT, input.kind(), input.text(), payloadJson, null, now()));
```
`step` (spec 017 FR-003) can only ever be set by `RelayService#postFounderTurn` -- the founder's
own `POST /v2/projects/{id}/relay`. `POST /v2/agent/relay` (`AgentDtos.RelayTurnInput`) has no
`step` field on its own request shape at all, so there is no way for an agent host to echo the tag
even if it wanted to.

**Consequence, live-confirmed**: `keel-web`'s `lib/relayTurns.ts#turnsForStep` filters BOTH
founder and agent turns by exact `step` match, and `components/chat/GuidedStep.tsx`'s `StepTurn`
renders a real "agent" branch (the Keel mark, `AgentText`/`PlaybackRender`) for whatever turn shows
up inside that filtered list. Since an agent turn's `step` is always `null`, that branch can never
actually render from any wire response the shipped protocol can produce -- the guided step's own
overlay only ever shows the founder's half of a conversation, never the agent's reply to it, no
matter how the agent behaves. A founder who types a question into a guided step and gets an answer
from their agent will see that answer only in the general history drawer below, not under the
question it answers.

**Not applied, but the shape of a fix**: give `POST /v2/agent/relay`'s turn input an optional
`step`, mirroring the founder endpoint, and have `RelayService#appendAgentTurn` carry it through
instead of hardcoding `null`; a real host would then echo whichever step the founder turn it is
answering carried. This scenario does not assert around the gap: it only ever checks that the
founder's own line lands inside the step's own exchange (`evals/test_s001_smoke.py`), never that
an agent reply does.

**#13 RESOLVED 2026-08-31**: keel-cloud 35df2d8 — RelayTurnInput gains step, service passthrough,
served bridge echoes the founder's marker onto replies (version 2). The step overlay's agent
branch can now fire from real wire responses.

## Retirement note, 2026-09-03 (005-connect-stack)

The stack this repo referees changed underneath it: keel-skill is archived, the relay is no
longer a founder surface, and every judgement now runs as an inference job through the founder's
own keel-runtime, connected by device code through keel-connect-skill and confirmed in keel-web.
Retired in this pass (git history has all of it, nothing here is lost):

- The agent-protocol half of the harness and its tests: `harness/driver.py`, `mcp_client.py`,
  `bridge.py`, `relay.py`, `founder_sim.py`, `agent_session.py`, `shaping_scoring.py`, and
  `tests/test_bridge.py`, `test_relay.py`, `test_founder_sim.py`, `test_shaping_scoring.py`,
  `test_policy_v5.py`.
- The old scenario set S-002..S-011 (`evals/test_s002_pricing_pivot.py` through
  `evals/test_s011_relay.py`), the shaping gauntlet's Layer 2 (`evals/test_shaping_gauntlet.py`,
  `make eval-shaping`, the `shaping` pytest marker), and the scenario-sharing modules
  `evals/recipes.py`/`evals/scenario.py` they depended on.
- Everything above is replaced by one scenario, S-001, rewritten from scratch against the
  connect stack (spec `005-connect-stack`) -- the whole payroll-exceptions journey, once,
  deterministic, no LLM.

Findings #1-#13 above describe the retired protocol's own stack (agent-protocol MCP/relay,
policy v2-v5) and are kept for the historical record; none of them are re-asserted by S-001
unless independently reproduced against the connect stack. The MCP-reachability workaround
(finding #3) and its `SPRING_AI_MCP_SERVER_PROTOCOL` override no longer apply -- the connect
stack talks to keel-cloud over `/v2/*` and keel-runtime's own long-poll, never MCP.

## 14. Non-blocking (worked around): keel-web's overview/stage routes can bounce forever right
## after a stage's beliefs land

**Severity**: non-blocking -- worked around in the harness (a hard reload), but a real founder
hitting this gets a permanently blank screen with no recovery affordance of their own short of
reloading by hand, which nothing on screen suggests doing.

**Where**: `keel-web` `src/routes/founder/OverviewRoute.tsx` (~line 33) and
`src/routes/founder/StageRoute.tsx` (~line 68-79).

```tsx
// OverviewRoute.tsx
if (pending?.screen === ASSUMPTIONS_SCREEN[current] && pending.status === "AWAITING_CONFIRMATION") {
  return <Navigate to={`/p/${projectId}/s/${current}`} replace />;
}
```

```tsx
// StageRoute.tsx
if (!summary.framed) {
  if (isDraftReady) {
    if (draft.isPending) return <Loading label="Loading the review…" />;
    if (draft.error) return <ErrorNotice error={draft.error} />;
    if (draft.data && isProposedCard(draft.data.proposed)) {
      return <DraftReview .../>;
    }
  }
  // Not yet ready to review — the walk (GuidedStep, mounted from the overview) is where this
  // stage lives right now.
  return <Navigate to={`/p/${projectId}`} replace />;
}
```

Both routes decide whether the chained assumptions interaction is ready to review from their
**own, independent** `useOverview(projectId)` read. Live-confirmed (this repo's own S-001 smoke,
first cold run after the walk saves the problem statement and lands C8): `OverviewRoute` reads
`AWAITING_CONFIRMATION` and navigates to `/p/:id/s/PROBLEM`; `StageRoute` mounts, its own
`useOverview` read disagrees (still transitioning), so `isDraftReady` is false and it navigates
straight back to `/p/:id`; `OverviewRoute` mounts again, reads `AWAITING_CONFIRMATION` again
(nothing about the disagreement resolves itself), and navigates back -- forever. Browser console:

```
Warning: Maximum update depth exceeded. This can happen when a component calls setState inside
useEffect, but useEffect either doesn't have a dependency array, or one of the dependencies
changes on every render.
    at Navigate (react-router-dom.js:7500:3)
    at OverviewRoute (src/routes/founder/OverviewRoute.tsx:25:33)
```

`<div class="shell__main"></div>` stays empty indefinitely -- no loading state, no error, nothing
a founder could act on; the only way out is a manual full reload, which happens to force both
routes to refetch from one consistent snapshot and breaks the bounce.

**Reproduction**: `make up && make eval K=s001` from cold, first time the walk saves the problem
statement (`Chat.save_confirmation()`) and the app is left to auto-navigate to the review. Bundle:
`runs/20260903T212843Z-s001-smoke/` (`failure/console.log` has the repeating warning;
`failure/page.html` shows the side nav on `/p/<id>/s/PROBLEM` with an empty `shell__main`).

**Why the scenario was adapted, not routed around**: `harness/browser.py`'s `Chat.wait_for_review`
now reloads the page every 4s while it waits for `.card.openc` -- the same recovery a founder
stuck on this screen would reach for, not a contortion around what the wait is testing (the
review card actually rendering with the right claim). The scenario still asserts the real
content once it appears.

**Shape of a fix, not applied here**: give the two routes one shared source of truth for
`pendingInteraction` readiness (a single `useOverview` call lifted to a shared ancestor, or a
`staleTime`/`refetchOnMount` policy that keeps both reads from ever observing different
snapshots of the same interaction), and render a loading state instead of an immediate `Navigate`
the first time `isDraftReady` reads false right after arriving from the overview's own redirect
-- so a genuine transition window degrades to a spinner, never a bounce.

**#14 RESOLVED 2026-09-03**: keel-web `ccf822c` — the stage route holds a "Recording…" state on
the transient after approve instead of redirecting to the overview. `harness/browser.py`'s
`Chat.wait_for_review` no longer reloads; it is the plain positive wait on `.card.openc` again.

## 15. Non-blocking (worked around): the just-approved stage card renders empty until reloaded --
## the stage-card query is never invalidated on confirm

**Severity**: non-blocking -- worked around in the harness (one reload, only where the walk reads
the just-approved card without an intervening full navigation), but a real founder who approves
the final stage lands on a card with no claim, no belief groups, and no "Go to People" / "See the
overview" note -- no visible way onward short of a manual reload, which nothing on screen suggests.

**Where**: `keel-web` `src/api/interactions.ts` (`useConfirmInteraction`, ~line 88-99) versus
`src/api/founder.ts` (`useApproveStage`, ~line 97-110) and `src/api/queryKeys.ts` (~line 5-6).

```ts
// src/api/interactions.ts -- the mutation actually wired to DraftReview's own
// "These are right -- approve" button (StageRoute.tsx: `useConfirmInteraction(projectId,
// interactionId)`, `confirm.mutate()`).
export function useConfirmInteraction(projectId: string, interactionId: string) {
  return useMutation({
    mutationFn: () => interactionRequest<InteractionView>(
      `/v2/inference-interactions/${interactionId}/confirm`, { method: "POST" }),
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.interaction(result.interaction_id), result);
      void queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.interactionsForProject(projectId) });
      // no invalidation of queryKeys.stage(projectId, stage) -- the sibling mutation right below
      // in founder.ts does invalidate it; this one does not.
    },
  });
}
```

```ts
// src/api/founder.ts -- a second, apparently-unused-by-this-flow approval mutation that DOES
// invalidate the stage-card query correctly.
export function useApproveStage(projectId: string, stage: StageType) {
  return useMutation({
    mutationFn: (expectedRevision: number) => ... ,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.overview(projectId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.stage(projectId, stage) });
    },
  });
}
```

`queryKeys.overview` and `queryKeys.stage` are distinct top-level keys (`["project", id,
"overview"]` vs `["project", id, "stage", stage]`, `src/api/queryKeys.ts`), so invalidating one
never invalidates the other.

`StageRoute.tsx` mounts `useStageCard(projectId, stage)` unconditionally (line 60), before the
stage is framed -- while the card is still a draft, this fetch already runs and caches keel-
cloud's empty pre-approval shape (`{claim: null, groups: []}` in effect) under that query key.
Once `confirm.mutate()` succeeds, the overview's own (correctly invalidated) refetch flips
`summary.framed` to `true` and `StageRoute` switches from `DraftReview` to `ApprovedCard` -- but
`stageCard.data` is still the never-refetched, cached empty draft-time response, so `ApprovedCard`
renders with no claim and no belief groups. Live-confirmed on the fourth (final) stage
specifically: `ApprovedCard`'s closing "Go to People" / "See the overview" note only renders when
`!readOnly && nobodyAskedYet` (`StageRoute.tsx` ~line 303), and with an empty card the
`readOnly`/`nobodyAskedYet` computation itself reads a state that never shows that note -- the
onward door is simply gone, indefinitely, no matter how long anything waits.

**Reproduction**: `make up PROFILE=playground && make eval K=s001 PROFILE=playground` from cold,
first time COMMERCIAL (the fourth, final stage) is approved. Bundle:
`runs/20260904T011114Z-s001-smoke/` (`failure/page.html` shows `<div class="card openc">` for
"Will they pay" with the approved kicker but no `<p class="claim">`, no belief groups, and no
`approved-note`/`actions`; `screenshots/039-stage-commercial.png` shows the same card fully
populated, in review, one screenshot earlier -- the content plainly exists server-side and is
simply never re-fetched client-side).

**Why the scenario was adapted, not routed around**: `harness/browser.py`'s `StageCard.
go_to_people` now checks for the link once and, only if it is absent, does one reload (mounting a
fresh query client, which reads the now-framed card correctly) before trying again -- the same
recovery a founder stuck on this screen would reach for. Every other read of an approved card in
this smoke goes through `StageCard.open()`, which always does a full `page.goto` and was never
affected.

**Shape of a fix, not applied here**: add
`void queryClient.invalidateQueries({ queryKey: queryKeys.stage(projectId, stage) })` to
`useConfirmInteraction`'s `onSuccess` in `src/api/interactions.ts`, matching what `useApproveStage`
already does in `src/api/founder.ts` -- or gate `useStageCard`'s query on `enabled: summary?.
framed` so it never caches the pre-approval empty shape in the first place.

**#15 RESOLVED 2026-09-04**: keel-web `6912f7e` -- the confirm mutation now invalidates the whole
project query prefix (not just the overview key), so the just-approved stage card refetches and
renders correctly without a reload. `harness/browser.py`'s `StageCard.go_to_people` no longer
reloads; it waits on the link directly.

## 16. Non-blocking (alternate path): the approved card's onward doors -- R4's *Continue to step N*
## and S4's *Go to People* -- can never render, because keel-web keys them off `verdict` being
## absent and keel-cloud always sets it once a stage is approved

**Severity**: non-blocking -- the founder still has a door (the side nav's *People* entry
unlocks the moment every framed card is approved, journeys §1.4 / the three-section navigation
amendment), and the harness takes that door; but the walk's own designed onward buttons never
appear, so a founder who does not think to look at the nav is left on an approved card with
nothing telling them what to do next.

**Where**: `keel-web` `src/routes/founder/StageRoute.tsx` (~line 235, ~line 296-320) against
`keel-cloud` `src/main/java/com/keeldiscovery/cloud/protocol/founder/FounderViewAssembler.java`
(line 92).

```tsx
// StageRoute.tsx
const nobodyAskedYet = summary.verdict === undefined && !(summary.peopleAsked ?? 0);
...
{!readOnly && nobodyAskedYet ? (isFinalStage ? <S4 note: See the overview / Go to People →>
                                             : <R4: Continue to step N — … →>) : null}
```

```java
// FounderViewAssembler.java, the StageSummary the overview carries
String verdict = approved ? project.verdictOfStage(type).name() : null;
```

The two disagree about what "nobody asked yet" looks like on the wire: keel-cloud sets
`verdict` to `"UNTESTED"` for every approved stage (it is `null` only *before* approval), so on
the approved card `summary.verdict === undefined` is always false and the whole onward block is
skipped -- for every stage, every time. keel-web's own visual fixtures (`tests/visual/states/
stages.ts`) omit `verdict` for their approved-nobody-asked states, which is how the mock renders
the R4/S4 buttons the walk was designed around.

**Reproduction**: `make up && make eval K=s001` from cold, then read the overview directly:

```
GET /v2/projects/<id>/overview   (founder session)
{"type":"COMMERCIAL","framed":true,"approved":true,"verdict":"UNTESTED","need":"INVITE",
 "peopleAsked":0,...}
```

Bundles `runs/20260903T222459Z-s001-smoke/` and `runs/20260904T012511Z-s001-smoke/` (the
second after keel-web `ccf822c`, and after a full reload of the approved card): `failure/page.html`
in each is the approved COMMERCIAL card with the side nav's People link unlocked
(`href="/p/<id>/people"`) and no *Go to People* text anywhere -- 15s and 30s waits for it both
time out. The same rule is why no *Continue to step N* link ever rendered after the PROBLEM or
SOLUTION approvals in any run today (`harness/browser.py`'s `StageCard.continue_to_next_step`
fell back to the overview -- the link's own destination -- each time).

**Why the scenario takes the alternate path**: the side nav's People entry is the product's own
second door to the same place, and its unlocking *is* the S4 moment's promise ("People unlocks");
the smoke asserts the unlock and walks through it (`Shell.open_people`). The S4 three-part note's
own text is not asserted, since it cannot render.

**Shape of a fix, not applied here**: `nobodyAskedYet` should read `!(summary.peopleAsked ?? 0)`
alone (or `summary.verdict === "UNTESTED"` beside it), matching what keel-cloud actually sends;
alternatively keel-cloud's `StageSummary.verdict` could stay `null` until someone has been asked --
but the wire contract (`openapi-v2.yaml`) already documents `verdict` as present once approved,
so the client is the side that drifted.

**#16 RESOLVED 2026-09-04**: keel-web `6912f7e` -- `nobodyAskedYet` no longer tests for an absent
`verdict`. R4's *Continue to step N* and S4's *Go to People →* render again; `harness/browser.py`'s
`StageCard.go_to_people` is a real method again (waits on the link, no side-nav reroute), and
`evals/test_s001_smoke.py`'s S4 section clicks it directly while still asserting the People
unlock separately.

## 17. RESOLVED -- was BLOCKING (spec 006-agent-optional's own stated prediction, confirmed): the read action is
offered with no agent connected, refused only after the click, with the refusal never rendered

**Severity: blocking** for US1 acceptance scenario 3 ("the founder is never left to discover it by
refusal") -- a founder with no runtime running and an unread answer clicks *Have your agent read
the N new answers*, the request is refused on the wire, and nothing on the screen tells them why
nothing happened. This is exactly the failure `specs/006-agent-optional/spec.md`'s own "What I
expect this to find" section named in advance, written before the scenario ran, and it is
confirmed, not refuted.

**Where**: `keel-web` `src/routes/founder/PeopleRoute.tsx` (~line 207): the button's own gate is

```tsx
<button
  type="button"
  className="btn primary"
  disabled={unreadCount === 0 || startReadings.isPending}
  onClick={() => startReadings.mutate(undefined, { onSuccess: (created) => setBatchId(created.batchId) })}
>
```

`unreadCount`/`startReadings.isPending` are the only two facts this disables on -- `me.data?.agent
.connected` (already fetched by `ProjectShell`'s own `useMe({poll:true})`, and rendered right next
to this same button as the agent line) is never consulted here, and `useStartReadings`'s mutation
carries no `onError` handler at all, so a refused click has no visible consequence whatsoever --
the button just goes back to normal, indistinguishable from having done nothing.

Against `keel-cloud` `src/main/java/com/keeldiscovery/cloud/protocol/founder/
FounderErrandController.java` (~line 138), which gates exactly the way `POST /v2/projects` does
(the founder API's own guarantee, correctly implemented on the wire):

```java
@PostMapping("/readings")
ResponseEntity<FounderDtos.ReadingBatch> startReadings(HttpServletRequest request,
        @PathVariable String projectId) {
    ...
    DomainException.rejectIf(!isConnected(founderId, keelSessionId), "agent", "your agent is not connected",
            "run keel connect and approve it, then try again");
```

**Reproduction**: `make eval K=s002 PROFILE=playground` (either after an S-001 run in the same
session, or from cold) -- `runs/20260904T032807Z-s002-agent-optional/` is the run bundle (score
2.0/5, `failed_step`: "§1.5/§1.6: the read action is disabled and states why, with no agent").

Screen evidence, `screenshots/026-people-who-tab.png` (People, no agent connected, Priya Raman's
answer sitting unread): the *Have your agent read the 8 new answers* button renders plain and
enabled, with no mention anywhere of the agent line reading *No agent connected* three inches
above it. `harness/browser.py`'s `People.read_action_state()` reads it back as
`{"present": true, "enabled": true, "label": "Have your agent read the 8 new answers", "reason":
"Reading is what moves the cards. Until your agent has read an answer, it counts for nothing on
the overview — but you can always see it yourself."}` -- that "reason" text is the button's own
*always-there* explainer, not an agent-connection reason; it renders identically whether an agent
is connected or not.

Wire evidence, the same run, immediately after clicking that same button
(`screenshots/027-people-read-clicked-refused.png` -- indistinguishable from the screen just
before the click):

```json
{"request": {"POST": "/readings"},
 "response": {"status": 422,
              "body": {"rule": "agent", "problem": "your agent is not connected",
                       "remedy": "run keel connect and approve it, then try again"}}}
```

The screen and the wire, side by side: the API refused the exact request the button issued, and
the screen shows nothing at all about it -- no error, no banner, no change to the row, no change
to the button. The founder has no way to learn why "nothing happened."

**Why the scenario was not adapted around it**: this repo owns no product code -- the scenario's
own assertion (`evals/test_s002_agent_optional.py`, "§1.5/§1.6: the read action is disabled and
states why, with no agent") states the guarantee US1 acceptance scenario 3 promises, and fails
honestly against the real screen. `read_action_state()` (`harness/browser.py`) was written to read
whatever the screen actually shows, not to assume a disabled state exists.

**Shape of a fix, not applied here**: `PeopleRoute.tsx`'s button should also gate on `me.data?.
agent.connected` (or an equivalent prop threaded down from `ProjectShell`), with a reason beside it
the same way `LandingRoute.tsx`'s L4 already does (`LANDING_LOCKED_REASON`, `.locked .why`) --
`"Needs your agent — run keel connect to read answers"` or similar, next to the button rather than
replacing the always-there hint. `useStartReadings` should also grow an `onError` (or the caller
should render `isApiError(startReadings.error)` via `RemedyBanner`, the same pattern
`NameProjectStep` already uses for the equivalent `POST /v2/projects` refusal), so a refusal that
does reach the wire is never silent either.

**#17 RESOLVED 2026-09-04**: keel-web `cadbc19` -- `PeopleRoute.tsx` now reads the agent state from
`useMe` and disables the read action with the reason beside it (`translate.ts`
`READING_LOCKED_REASON`: "Needs your agent -- run keel connect to read them") whenever no agent is
connected; the wire's own `rule: agent` refusal, if it ever arrives, renders as a `RemedyBanner`
instead of vanishing. Confirmed by `20260904T034746Z-s002-agent-optional` (passed): the
"§1.5/§1.6: the read action is disabled and states why, with no agent" step records
`{enabled: false, reason: non-empty}`.

## 18. RESOLVED -- was non-blocking: a reading batch's completion toast reappears on every later visit to People,
not only "just after it finished"

**Severity: non-blocking** -- cosmetic and confusing (a founder can read a stale "things moved"
toast and wonder what just happened), never blocking; no data is at risk.

**Where**: `keel-web` `src/routes/founder/PeopleRoute.tsx` (~lines 53-65):

```tsx
useEffect(() => {
  const running = runningBatches.data?.find((b) => b.status === "RUNNING");
  const latest = running ?? runningBatches.data?.[0];
  if (latest && !batchId) setBatchId(latest.batchId);
}, [runningBatches.data]);

useEffect(() => {
  if (batch.data?.status === "DONE" && batch.data.summary) {
    showToast({ message: batch.data.summary, linkTo: `/p/${projectId}`, linkLabel: "See the overview →" });
  }
}, [batch.data?.status]);
```

The comment beside the first effect names its own intent precisely ("the most recently finished
[batch], so the toast ... still greet the founder even if the batch completed the moment before
this load") -- but nothing distinguishes "completed the moment before this load" from "completed
days ago, already seen and dismissed." Every fresh mount of `PeopleRoute` re-adopts the most
recently *finished* batch (there is no once-per-batch "seen" flag, in state or storage) and the
second effect fires `showToast` again, every time, for as long as that batch stays "the most
recent."

**Reproduction**: live-confirmed twice in the same S-002 run
(`runs/20260904T032807Z-s002-agent-optional/`), on People visits that followed a logout+login and
did nothing to trigger a new read:
- `screenshots/026-people-who-tab.png` -- opening People fresh shows *"✓ Nothing moved. See the
  overview →"* immediately, from a batch this visit never started.
- An earlier run on the same project (`runs/20260904T031029Z-s002-agent-optional/screenshots/
  027-people-read-clicked-refused.png`) shows the same thing with a different stale message
  ("Four things moved on the problem card...") right after a click that was itself *refused*
  (see #17) -- the toast on screen has nothing to do with the request that just ran.

This is also the specific edge case `specs/006-agent-optional/spec.md` names in advance ("The
stale toast: a completion toast from before the logout must not reappear after login") --
confirmed reappearing, though not only across a logout boundary: any later People visit re-shows
it.

**Why the scenario was not adapted around it**: found incidentally while gathering #17's own
screen evidence; not (yet) asserted on directly by `evals/test_s002_agent_optional.py`, since #17
already stops the scenario first on every run to date. Recorded here rather than left
undocumented.

**Shape of a fix, not applied here**: track which batch id's toast has already been shown (a ref,
or a small "last-toasted batch id" piece of state persisted alongside `batchId`) and only fire
`showToast` the first time a given batch is observed `DONE`, not on every mount that happens to
adopt it as "most recent."

**#18 RESOLVED 2026-09-04**: keel-web `cadbc19` -- the completion toast fires once per batch id
(`sessionStorage` key `keel.reading-toast.<batchId>`), so a later visit to People that adopts the
most recent `DONE` batch as its query no longer re-shows it. Confirmed by
`20260904T034746Z-s002-agent-optional`: no stale toast after the re-login.

## 19. RESOLVED -- was non-blocking (worked around: log out and back in): a runtime that reconnects using its own
still-valid stored credential never rebinds the founder's already-open keel session

**Severity: non-blocking** -- a real founder can still reach a connected state (by logging out and
back in, which S-001's own arrival already proves works), but the UI offers no path to it and no
explanation, so a founder who restarts `keel connect` while still logged in has no way to make
the agent line go green short of guessing to log out.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/application/KeelSessionService.java`
-- binding a keel session to a live agent happens in exactly two places, `open()` (login) and
`bind()` (explicit device approval):

```java
public Opened open(UserId userId) {
    ...
    Optional<AgentSession> live = agentSessions.mostRecentLiveFor(userId, now.minus(presenceThreshold));
    live.ifPresent(agentSession -> bindings.upsert(new SessionBinding(session.id(), agentSession.id())));
    return new Opened(session, live.map(AgentSession::id).orElse(null));
}
```

Neither runs when `keel-connect-skill`'s own script reconnects a still-valid, persisted credential
(`keel_connect_check.py --credential-backend file`) without a fresh device code -- the script's own
documented outcome for this is `"connected"`/`"already_connected"` (`harness/connect.py`'s own
`start_runtime_via_skill`/`reconnect` accept both), and neither mints a `verification_uri` to
approve. `keel-web`'s bare `/connect` entry (`src/routes/connect/ConnectRoute.tsx`'s `ScreenD`)
offers no affordance for this case either -- just a code-entry box and the browser's own current
(still-disconnected) state; there is no "we noticed a runtime is already talking to us, bind it?"
option anywhere.

**Reproduction**: `runs/20260904T031913Z-s002-agent-optional/transcript.jsonl` (a run against
`evals/test_s002_agent_optional.py` before it grew the log-out/log-in fallback below) -- seq 45,
`keel-connect-skill: reconnect the runtime` returns `{"outcome": "connected", "agent_session_id":
"0d2ff964-...", "pid": 75295}`; seq 96, over 150 seconds and dozens of `/v2/me` polls later (the
same browser session, never having logged out again), `"§1.0: New project is live again, agent
reconnected"` still reads `{"agent_connected": false}`. The keel session opened at re-login (US1
step 2, before the runtime was restarted) never gains a `session_binding` row, and nothing
re-derives one later no matter how long the reconnected agent keeps heartbeating.

**Why the scenario was adapted around it**: `evals/test_s002_agent_optional.py`'s own step 7
branches on `reconnect()`'s outcome -- `"authorization_started"` drives the browser approval flow
(frame B) exactly as arrival does; any other outcome logs out and back in (`Auth.log_in` again),
which is the one path this repo could confirm actually works (`KeelSessionService.open`'s own
auto-bind), and records a `DRIFT evidence` step showing the pre-workaround state
(`agent_connected: false`) first. This is a real, live-confirmed product gap, not silently patched
around: the harness takes the same door a real founder would eventually have to find themselves.

**Shape of a fix, not applied here**: either (a) `keel-web`'s `/connect` bare entry could offer a
"you have a live runtime — reconnect it" action when `GET /v2/me` shows a founder-owned agent
session exists but is unbound, calling a new or existing `bind()`-shaped endpoint without a device
code at all, or (b) `POST /v2/me` (or a lightweight poll) could re-run the same "most recently
seen live agent" auto-bind `open()` already does, on demand, so a still-open keel session can pick
up a runtime that came back without forcing a fresh login.

**#19 RESOLVED 2026-09-04**: keel-cloud `633c1ac` -- `AgentSessionService.create` now binds the new
agent session to the founder's most recent ACTIVE keel session as well as to the one that approved
the credential (the approving session stays bound, spec 020 FR-013), so a runtime that comes back
from its stored credential turns the already-open landing green on its own; pinned end to end by
`KeelSessionBindingTest.aRuntimeThatStartsAfterANewLoginBindsToTheSessionThatIsOpenNow`. The
scenario's logout/login fallback is gone: `evals/test_s002_agent_optional.py` now waits (≤40s) for
the open landing to read connected and fails the run if it never does. Confirmed by
`20260904T041459Z-s002-agent-optional` (passed, 5.0/5 under policy v7): the step "§1.0: a silent
reconnect binds the keel session that is open now (DRIFT #19)" records `agent_connected: true`.

## 20. RESOLVED -- was non-blocking: an unknown path inside a project renders the shell with an empty main pane
and no words -- a founder on a stale bookmark gets chrome and silence

**Severity**: non-blocking -- the side nav still works, so the founder can click their way out,
but nothing tells them the page they asked for does not exist; the top-level not-found page
("This page doesn't exist.") never renders for a child path.

**Where**: `keel-web` `src/routes/AppRoutes.tsx:29-38` -- the nested `<Routes>` under
`/p/:projectId/*` has `index`, `people`/`invite`/`invitations`, `brief` and `s/:stage`, and no `*`;
`ProjectShell` renders its `.shell__main` with no matching child, so the pane is empty.

**Reproduction**: `runs/20260904T082121Z-s003-every-door/` (the first S-003 run, keel-web
`9771dd7`), probe step "probe: unknown path inside the project (/p/<id>/nope)" --
`{"verdict": "blank", "detail": "the shell rendered with an empty main pane"}`; screenshot in the
bundle. The same run opened all 63 rendered doors on 12 seeds and every one opened (D1-D3 clean);
the top-level `/nope` rendered the not-found page; `/p/<id>/s/NOPE` redirected to the overview;
`/i/nope` rendered the not-found page on the wire's own 404.

**Shape of a fix**: a nested `*` route rendering the not-found copy *inside* the shell, in the
house voice, with the side nav still usable -- keel-web spec `008-every-door` F1
(design `every-door-design.md` §5).

**Also noted, not observable by the walk**: `index.html` declared no icon, so a real browser
requests `/favicon.ico` on every load and gets a 404 (design §5 F2). Headless Chromium under
Playwright never requests favicons, so the walk's response listener cannot see it either way;
the fix (an inline SVG icon) is verified by inspection of `index.html`, not by this run.

**#20 RESOLVED 2026-09-04**: keel-web `71c045a` (spec 008) -- a nested `*` route renders "This
page doesn't exist. Your project is still here — pick a step on the left." inside the shell, side
nav intact, and `index.html` declares an inline SVG icon. Confirmed by
`20260904T082453Z-s003-every-door` (passed, 5.0/5 under policy v7; FIDELITY and GUIDANCE not
applicable to a walk): the probe reads `not_found` inside the shell, and all 63 doors on 12 seeds
open.

## 21. RESOLVED -- was non-blocking (live-confirmed): a reading that answers `NEEDS_INPUT` has no screen -- the
founder sees "reading..." until the harness gives up

**Severity**: non-blocking today (the scripted executor never asks on INTERPRET), real the moment a
live agent does: keel-cloud's INTERPRET contract allows `NEEDS_INPUT` ("a claim's meaning turns on
something only the founder can resolve", `keel/inference-instructions/interpret.md`), the
orchestrator moves the interaction to `AWAITING_INPUT`, and keel-web's People page -- which drives
readings as a batch behind *Have your agent read them* and waits for the batch's toast -- renders
no question and no way to answer one.

**Where**: `keel-cloud` `application/ScreenResponseContracts.java` (`ALLOWED_OUTCOMES` is the same
two for every screen, INTERPRET included); `keel-web` `src/routes/founder/PeopleRoute.tsx` (the
batch poll knows `DONE` and refusal, not a question).

**Reproduction**: `runs/20260904T092257Z-s004-stranger-who-gives-orders-live/` -- the first live
S-004 run, keel-runtime `fe2f204`. The stranger's answers were orders, not answers; the live model
(correctly refusing to follow them) applied the executor's then-too-broad system-prompt rule
"if the source material does not answer the question, respond NEEDS_INPUT" to the *reading*, and
the job's envelope (`$KEEL_HOME/jobs/1ba92710-.../envelope.json`) reads `outcome: NEEDS_INPUT`,
`questions: [{"question": "This box is for the participant's own answers to the interview
questions..."}]`. Step 43, "founder has the agent read the new answers", timed out after 240 s
waiting for `.toast[role='status']`. Every one of the six envelopes in that run has
`permission_denials: []`, `num_turns: 2`, `is_error: false`, cost $0.05-0.08 -- the line held; only
the reading's shape did not.

**Two things, separately**: (1) the executor's rule was wrong for readings -- fixed in keel-runtime
(`SYSTEM_PROMPT`: a reading records that words which do not answer count for nothing and
completes; it never asks on a stranger's behalf), so a live reading of orders now completes with
empty evidence, which is the instruction's own "nothing counts here" path. (2) The product still
has no screen for the case the instruction *does* permit (an ambiguous product term). Not worked
around here.

**Shape of a fix, not applied here**: either (a) INTERPRET's allowed outcomes drop `NEEDS_INPUT`
and the instruction's one asking case becomes "record the claim against both readings with a
note" -- one shape, no new screen, in the spirit of the MVP's simplifications -- or (b) People
learns to show a reading's question beside the person's row and take the founder's answer. The
founder's call.

**#21, the executor half, RESOLVED 2026-09-04**: keel-runtime `64c2aaf` -- the system prompt's
asking rule now applies only to framing the founder's own text; a reading records that words which
do not answer count for nothing and completes. Confirmed by
`20260904T093551Z-s004-stranger-who-gives-orders-live` (passed, 5.0/5): the reading of a
participant whose every answer was an order came back `COMPLETED` with empty evidence, the toast
read "Nothing moved.", the card's standing was unchanged; six live jobs, $0.37 in all, every
envelope `permission_denials: []`, `num_turns: 2`; the canary token appeared nowhere and its file
was untouched. **The product half stays open** (a screen for the one asking case INTERPRET still
permits) -- the founder's call between (a) and (b) above.

**#21 RESOLVED 2026-09-04**: the founder chose (a). keel-cloud `88b4912` (spec 026 FR-010) -- a
reading has one outcome, `COMPLETED`; its contract carries no question schema, and the
instruction's asking case is now a `NEUTRAL` claim that says what could not be settled. Confirmed
by `20260904T114959Z-s002-agent-optional` (scripted reading, 5.0/5) and
`20260904T115336Z-s004-stranger-who-gives-orders-live` (live reading of a stranger's orders,
5.0/5, "Nothing moved.", no tool tried, canary silent).

## 22. RESOLVED -- was non-blocking (found by the founder by hand): the chat body hides what does not fit -- a tall
confirmation card is clipped under the header and nothing scrolls

**Severity**: non-blocking for the scripted smoke (its statements are short), real with a live
agent: the founder could not read the first lines of the claim they were asked to save.

**Where**: `keel-web` `src/styles/app.css` -- `.chat__body { overflow: hidden }` with
`.chat__body .inner { position: absolute; bottom: 12px }`. The design of record says three times
that the body alone scrolls (screen-review-design.md §4.2 "Body", frame C4, U16).

**Reproduction**: the founder's screenshot of 2026-09-04 11:14 (a real `claude` on the problem
step): the card's opening lines cut under the header, no scrollbar. Not reproducible by the
scripted executor, whose statements fit; a referee assertion would need a long-statement script
variant -- not added, the fix is a CSS rule and the guarantee's baselines pin the layout.

**Shape of a fix**: keel-cloud `canon/designs/the-card-says-what-it-knows-design.md` §2; keel-web
spec `011-the-body-scrolls`. Held until the founder finishes testing.

## 23. RESOLVED -- was non-blocking (found by the founder by hand): "Still unknown" repeats the last question the
agent asked, even when the founder answered it

**Severity**: non-blocking -- nothing is lost (the answer is in the statement) -- but the card
contradicts its own statement and puts a question under a closed composer.

**Where**: `keel-cloud` `application/InferenceOrchestrator.lastAskedQuestion` and spec 023's
judgement call 7: `ProposedStatement.note` is "the last question the agent asked, as the closest
founder-worded stand-in for still unknown". keel-web renders it as `Still unknown: <question>`
(`translate.ts` `confirmCardNote`).

**Reproduction**: the same screenshot -- the note reads "Where does this picture come from -- have
you done payroll approvals yourself…?", answered two turns earlier; the statement ends "based on
the founder's own 10 years in payroll".

**Shape of a fix**: drop the line; the statement names its own unknowns (every `*-frame.md`
already requires it). keel-cloud spec `027-the-card-says-what-it-knows`, keel-web spec `011`.
Held until the founder finishes testing.

## 24. RESOLVED -- was non-blocking (found by the founder by hand): a failed breakdown leaves the landed screen
counting forever, and Start over is refused without a word

**Severity**: non-blocking for the scripted smoke (its jobs never fail), wedging with a live agent:
the founder's step showed "Still working -- longer than usual" at 516 s on a job that had failed
at 73 s, and *Start over* did nothing.

**Where**: `keel-web` `src/components/chat/GuidedStep.tsx` -- the `childInteractionId` branch reads
`job.status` only to pick a phase (never `FAILED_STATUSES`), and a refused `cancelChild` renders
nothing. `keel-cloud` `InferenceOrchestrator.cancel` refuses any terminal row, and a `JOB_FAILED`
child is terminal, so the chain's live parent (`ACCEPTED`) could not be abandoned from the screen.

**Reproduction**: the founder's screenshots of 2026-09-04 11:28 (playground, a real `claude`);
`inference_interaction` rows `1f8c8ff4` (PROBLEM_FRAME, ACCEPTED) and `5390b269`
(PROBLEM_ASSUMPTIONS, JOB_FAILED); released by hand in the database.

**Shape of a fix**: keel-cloud spec 027 FR-006 (cancel abandons every live row of a chain);
keel-web spec 011 FR-008 (frame C10) and FR-010 (the refusal banner).

## 25. RESOLVED -- was non-blocking (found by the founder by hand): the breakdown job burns its turn allowance
trimming one field under a cap nobody told the model about

**Severity**: non-blocking -- the runtime reports the failure honestly -- but two real breakdowns in
a row failed (`error_max_budget_usd` at $0.258 against a $0.25 cap; then `error_max_turns` at
three turns against an allowance of two plus the CLI's retry).

**Where**: keel-runtime defaults (`KEEL_JOB_BUDGET_USD` 0.25, `KEEL_JOB_MAX_TURNS` 2); keel-cloud
`ScreenResponseContracts.RATIONALE_OR_NOTE_MAX` 600 with no instruction naming it.

**Reproduction**: an instrumented replay of job `e8ee292a` (`--output-format stream-json`): every
refused attempt was the same rule -- `/result/normalization_rationale: must NOT have more than
600 characters (got 704)`, then 640, then 613, then accepted; five turns, $0.38. The failure
message the cloud stored read only "the executor reported an error".

**Shape of a fix**: keel-cloud spec 026 FR-011 (the model is told the sizes; rationale cap 1 200);
keel-runtime spec 002 FR-009..011 (defaults 1.00 / 6, a failure that names the rule, one recovery
pass).

**#22-#25 RESOLVED 2026-09-04**: keel-cloud `30a19d5` (spec 027 + 026 FR-011: the note is gone from
the wire, `cancel` abandons every live row of a chain, every instruction names its sizes, the
rationale has room), keel-runtime `916583d` (defaults $1.00 / 6 turns, the failure names the rule
that was broken, one recovery pass), keel-web `bc1ab6f` (the body scrolls with auto-scroll, no
note, frame C10 for a failed breakdown, no empty promise while waiting, a refusal banner on Start
over). Confirmed by `20260904T162141Z-s001-smoke`, `20260904T162403Z-s002-agent-optional` and
`20260904T162527Z-s003-every-door`, all 5.0/5 on the merged stack.

## 26. Blocking: every `*_ASSUMPTIONS` job runs at keel-runtime's own 120 s timeout, and 6 of 21 exceed it

**Severity: blocking** for the assumption screens — a founder whose breakdown times out sees the
job fail, not a slow job. Nothing in this repo can work around it: the timeout is production's own
and the eval calls `ClaudeCodeExecutor` exactly as the runtime does, which is the point.

**Where**: `keel-runtime` `keel_runtime/executor.py`, `ClaudeCodeExecutor.__init__` line 331:

```python
    def __init__(
        self,
        binary: str = "claude",
        home: Path | str | None = None,
        budget_usd: float = DEFAULT_JOB_BUDGET_USD,
        max_turns: int = DEFAULT_JOB_MAX_TURNS,
        timeout_seconds: float = 120.0,
    ):
```

`keel_runtime/config.py` gives `DEFAULT_JOB_BUDGET_USD` and `DEFAULT_JOB_MAX_TURNS` overridable
homes and env lookups; `timeout_seconds` has neither. `get_executor` never passes it, so **120 s is
the number production ships and there is no way to change it without editing this line.**

**Reproduction**: `runs/20260906T170528Z-instructions-baseline/`, the 21 `*_ASSUMPTIONS` cases,
each one call through `ClaudeCodeExecutor` with keel-cloud's own exported contract and today's
instruction bytes. Wall clock per case, from `cases/<entry>/<stage>/run1/envelope.json`:

```
120s  07-mulchrun/SOLUTION       TIMEOUT      120s  05-paidly/PROBLEM         TIMEOUT
120s  05-paidly/COMMERCIAL       TIMEOUT      120s  04-linerly/PROBLEM        TIMEOUT
120s  02-compliancelog/COMMERCIAL TIMEOUT     120s  01-countly/COMMERCIAL     TIMEOUT
109s  01-countly/PROBLEM         ok           108s  04-linerly/SOLUTION       ok
108s  03-lullaby/SOLUTION        ok           107s  07-mulchrun/PROBLEM       ok
107s  05-paidly/SOLUTION         ok           106s  01-countly/SOLUTION       ok
 97s  07-mulchrun/COMMERCIAL     ok            97s  02-compliancelog/SOLUTION ok
 90s  06-repeatline/SOLUTION     ok            89s  06-repeatline/PROBLEM     ok
 87s  06-repeatline/COMMERCIAL   ok            87s  02-compliancelog/PROBLEM  ok
 86s  03-lullaby/COMMERCIAL      ok            85s  04-linerly/COMMERCIAL     ok
 81s  03-lullaby/PROBLEM         ok
```

**6 of 21 timed out — 29 %.** Of the 15 that finished, the slowest had **11 seconds of headroom**
and the median had 23. This is not a tail: the whole distribution sits against the limit.

Two things make it worse rather than better from here. keel-cloud spec 029's plan.md states
outright that the three assumption instructions **grow** — "a phrase table and a tense procedure
are added while two question paragraphs are removed" — and every one of these runs was against the
*old, shorter* prose. And a timeout is not a cheap failure: `01-countly/COMMERCIAL` had already
spent $0.28 of tokens when the 120 s elapsed, and that money buys nothing, because
`ExecutorTimeout` is raised before any result is read.

**Why the eval was not adapted around it.** The obvious workaround — pass `timeout_seconds=300` in
`instructions/runner.py` — was deliberately not taken. This eval exists to measure what production
sends and what production does with the answer; an eval with a longer timeout than production would
report an instruction as working that a founder would watch fail. The six timeouts are recorded as
`errored`, excluded from every quality metric, and named here instead.

**The shape of a fix, explicitly not applied** (keel-runtime's to make, not this repo's): give
`timeout_seconds` the same treatment `budget_usd` and `max_turns` already have — a
`DEFAULT_JOB_TIMEOUT_SECONDS` in `config.py` with a home/env override, threaded through
`get_executor`, and a default chosen against the measured distribution rather than a round number.
Whatever the number becomes, the finding stands on its own: the assumption screens are a
90-second-plus job today and are specified to get longer.

## 27. Non-blocking: `measure.per` is part of a `Measure` and part of no metric

**Severity: non-blocking** here, because it is a gap in this repo's own scoring rather than a
product defect — but it is recorded here because acting on it is keel-cloud's, in the shape of what
spec 029's instructions must teach.

**Where**: this repo, `specs/009-instruction-eval/contracts/metrics-contract.md`, the exact-match
table — it names `type`, `founderPhrase`, `measure.kind`, `measure.unit`, expected-or-band, `risk`
and `mark`, and **not `measure.per`**.

`keel-cloud` `domain/project/Measure.java` is a three-field record and its own Javadoc says so:
*"Two measures are equal when all three fields are — which is what `V2` checks when an observation
meets an expectation."* So a belief whose `per` differs from the golden one's is a **different
measure**, and an answer given against it places nowhere.

**Reproduction**: `runs/20260906T170528Z-instructions-baseline/`. Of 15 matched `INTERVAL` pairs,
**9 disagree on `per`** while scoring `unit` and expected-or-band as agreeing:

```
01-countly/PROBLEM      P3   golden per=incident   produced per=week
07-mulchrun/PROBLEM     P2   golden per=job        produced per=trip to the supply yard
07-mulchrun/PROBLEM     P3   golden per=day        produced per=working day
02-compliancelog/PROBLEM P1  golden per=(none)     produced per=person
04-linerly/COMMERCIAL   C9   golden per=year       produced per=single purchase
03-lullaby/COMMERCIAL   C10  golden per=month      produced per=month per paid baby app
06-repeatline/PROBLEM   P1   golden per=day        produced per=shift
03-lullaby/PROBLEM      P3   golden per=wake-up    produced per=night waking
02-compliancelog/PROBLEM P2  golden per=report     produced per=quarterly report
```

`01-countly/PROBLEM/P3` is the clearest: *one to two hours* **per incident** and *one to two hours*
**per week** are different claims about the same founder sentence, and today both score a clean
sheet on every field the contract names.

**Why the eval was not adapted around it.** Adding a `per` column is a metric definition change and
therefore a `MARKS_VERSION` bump, and the baseline had to be taken under version 1 or it could not
be compared with the runs that follow it. Doing it now would have made this run incomparable with
every later one, which is the one thing the versioning rule exists to prevent.

**The shape of a fix, explicitly not applied**: `per` becomes an eighth scored field alongside
`unit`, `MARKS_VERSION` goes to 2, and the baseline is re-scored from its own bundle rather than
re-run — `scorecard.json` and `cases/**/diff.json` already carry everything needed, which is what
the run-bundle contract's "re-reading" promise is for.

## 28. Non-blocking: a quarter of the corpus's `founderPhrase` values are reviewer's notes, not founder's words

**Severity: non-blocking**, and worked around here without touching the corpus — but recorded
because the corpus is frozen and a defect in a frozen artefact does not stop being one.

**Where**: `keel-cloud` `canon/designs/measured-beliefs/corpus/*.yaml`, the `founderPhrase` field.
**Twenty-two of the eighty-eight** carry a trailing parenthetical written for a human reviewer:

```yaml
founderPhrase: scans each delivery on arrival (the present-tense half, per §8.1 step 3)
founderPhrase: £40 a month per site (proxied by comparable spend, T1–T4 pass)
founderPhrase: adjust the spreadsheet manually (the founder implies it doesn't hold)
founderPhrase: not yet clear how much of that time is pure friction (a named unknown, given the standard pain proxy)
founderPhrase: flags a mismatch (the mechanism assumes the supplier is the cause)
```

The field's own definition is *the founder's own precision word, as they wrote it* — provenance, so
a review card can say *you said "about a week", which is 5 to 9 days*. A founder did not write *per
§8.1 step 3*; the corpus author did, explaining the decomposition to whoever read the file next.

**Reproduction**: `runs/20260906T195356Z-instructions/`, iteration 2 of the instruction eval.
`founderPhrase` scored 31.1 % over 61 matched pairs, and the misses were dominated by exactly this:

```
S11  golden 'scans each delivery on arrival (the present-tense half, per §8.1 step 3)'
     produced 'a phone app'
C15  golden '£40 a month per site (proxied by comparable spend, T1–T4 pass)'
     produced 'already pay for their POS and rota tools'
P6   golden "adjust the spreadsheet manually (the founder implies it doesn't hold)"
     produced ''
```

**No instruction can reproduce these**, and none should try — an instruction that emitted *"(the
present-tense half, per §8.1 step 3)"* onto the founder's review card would be worse, not better.
So 22 of 88 goldens were unmatchable on this field for a reason with nothing to do with the prose
being scored.

**Why the eval was adapted around it, and how.** The corpus is frozen (keel-cloud spec 029 SC-009)
and this repo never edits it. The metric was made fair instead: `instructions/align.normalise_phrase`
strips a **trailing** parenthetical **from the golden side, at comparison time**, so the two sides
are compared as the same kind of thing. `MARKS_VERSION` goes to 3 with judgement call 15, and the
earlier runs are re-scored from their own bundles rather than re-run. Nothing is softened: a phrase
that is wrong in front of the bracket is still wrong.

**The shape of a fix, explicitly not applied** (keel-cloud's, and only when the corpus is next
legitimately opened): move the annotation to a sibling key — a `note:` beside `founderPhrase` — so
the value holds what the founder wrote and the explanation still reaches the reader. The
seven-entry corpus would need twenty-two edits and its checker would not notice, which is exactly
why it should happen deliberately rather than as a side effect of a run.

## 29. Non-blocking: `Market`'s unit families are spelled inconsistently, and `M1` is a literal match

**Severity: non-blocking** — one refused belief set in one eval run, worked around in prose. But it
is a trap any author will fall into, because the rule reads as being about markets and is in fact
about spelling.

**Where**: `keel-cloud` `src/main/java/com/keeldiscovery/cloud/domain/project/Market.java`:

```java
    private static final Set<String> IMPERIAL = Set.of(
            "miles", "feet", "yards", "cubic yards", "inches", "pounds", "gallons");

    private static final Set<String> METRIC = Set.of(
            "km", "m", "cm", "kg", "g", "litres", "cubic metres");
```

The imperial family is spelled in **full words**; the metric family in **abbreviations**. `M1`'s
check is `unitFamily().contains(measure.unit())` — an exact set membership test, not a reading. So
`miles` is accepted and `kilometres` is refused, in favour of `km`.

**Reproduction**: `runs/20260906T220749Z-instructions/`, iteration 4, case
`04-linerly/PROBLEM/run1`. The instruction said to use "the word these people say, in this market's
family"; a London cyclist says *kilometres*; the aggregate refused the whole set:

```
M1: belief 'The rider covered at least fifty kilometres commuting by bike last week.' is measured
in kilometres, which is not a unit people use in GB — Fix: measure it in one of
[kg, cm, m, km, litres, cubic metres, g], or ask it of a role in a market that uses kilometres
```

The remedy line is worth reading twice: *"measure it in one of [… km …], or ask it of a role in a
market that uses kilometres"*. There is no such market. The refusal is telling the author their
market is wrong when their spelling is.

**Why the eval was not adapted around it.** A refusal is a refusal — it is a result the founder
would never have been shown, and softening it here would hide exactly what this eval exists to
find. The instructions were changed instead: all four unit vocabularies are now stated verbatim,
with the note that `M1` matches rather than reads (keel-cloud `4f39a4a`).

**The shape of a fix, explicitly not applied**: either spell both families as words (`kilometres`,
`metres`, `kilograms`) and normalise on the way in, or accept both spellings per unit. The second
is the smaller change and the first is the better one, because the unit is also what a participant
reads on their own form — and `km` is a label, not a word anybody says aloud. Either way `M1`'s
remedy text should name the spelling as the fix when the family is right.

## 30. RESOLVED -- was blocking: a respondent who writes no words counts nowhere, where the
corpus counts them hollow

**Severity: blocking** — it is the difference between S-006 and S-007 being green and being red,
and it is a disagreement between keel-cloud's aggregate and the frozen golden corpus, which the
whole of spec 010 exists to notice.

**Where**: `keel-cloud`, the aggregate's `guessed` count, against
`keel-cloud/canon/designs/measured-beliefs/corpus/05-paidly.yaml` and `07-mulchrun.yaml`.

The corpus says it in its own comment, on `01-countly` and again on `05-paidly`:

```
  # worked by hand: anchored people only count. 'guessed' is everyone shown hollow — a guessed
  # anchor (Marcus, Tom on A1/A2; Daniel, Lena on A3) and a blank one (Oliver on A1/A2; Tom on A3)
  # alike.
```

A **blank** anchor counts toward `guessed`. On the running product it does not — and, more than
that, a respondent who wrote nothing **anywhere** produces no reading job at all. keel-cloud's
People page says so in its own words the moment they answer: *"Nothing new to read."* Their picks
are stored, and they appear in no count on any card.

**Reproduction**: `runs/20260907T151620Z-s006-paidly` (`05-paidly`, twenty people). Yara Haddad
leaves `A1` and `A2` blank, taps *hasn't happened* on `A2b`, and still picks `S1`–`S5`. Every
translator belief comes back one guess short:

```
P1    guessed 2 vs 3        P2    guessed 2 vs 3        P3    guessed 2 vs 3
P4    guessed 2 vs 3        S5    guessed 2 vs 3
```

Same shape in `runs/20260907T152317Z-s007-mulchrun`, where Cody Brandt is the blank respondent —
there it also moves `inside`, because the corpus counts his picks and the product does not:

```
P1  inside 6 vs 7 | guessed 2 vs 3      P6  inside 6 vs 7 | guessed 2 vs 3
```

`01-countly` does not show it: its blank respondent, Oliver Grant, writes under the commercial
anchor, so he *is* read, and a blank anchor on a person who was read does count hollow.
`runs/20260907T145804Z-s005-countly` is green on every one of its eighteen standings.

**Whether the scenario adapted around it**: **no.** S-006 and S-007 assert the corpus's own
numbers and are red on exactly this. Softening the count would make the golden set agree with
whatever the product happens to do, which is the one thing a frozen corpus exists to prevent.

**The shape of a fix, explicitly not applied**: either the aggregate reads a submitted response
with no written anchor as an unanchored (hollow) observation on every belief its picks reach —
which is what the design's own key line promises the founder (*"one person, couldn't recall one —
shown, never counted"*) — or the corpus's simulator stops counting a blank as a guess and the
seven entries' `guessed` numbers are re-worked. The first is almost certainly right: a person who
answered the picks and skipped the story is exactly the person the hollow dot was drawn for. It is
keel-cloud's call, not this repo's, and the two must not be allowed to disagree quietly.

**FIXED 2026-09-07 in keel-cloud `da6d4bd`** (spec 030 follow-on, *an answer with no words in it
counts, hollow*): the first of the two shapes above, which is the one this entry argued for. A
reading is now required only where there are words -- `AnchorAnswer.hasWords`,
`Response.hasWordsToRead`, `Invitation.awaitsReading` -- and `Project.derive` no longer waits for a
reading that can never come: a response whose every anchor is blank or tapped derives whole the
moment it is stored, its picks kept as that person's observations and the standing showing them
hollow on every belief those picks reach. Confirmed on the running product:
`runs/20260907T163226Z-s006-paidly` stores Yara Haddad's response (she is on the People table, with
a *See Yara's answers* link of her own) and keel-cloud raises **no** reading job for her -- the
reading batch the founder starts for her is refused `NOTHING_TO_READ`, HTTP 409, which is keel-cloud
saying in its own voice that she has already been counted and there is nothing left to read.

**Not yet confirmed end to end, and deliberately not marked RESOLVED.** The numbers this entry is
actually about -- `guessed` 3 rather than 2 on `P1`-`P4` and `S5` -- have still never been read off
a screen or off the wire, because S-006 and S-007 now stop **earlier**, on the blank respondent, at
**#34**: keel-web offers to read the very answer keel-cloud has just decided needs no reading, and
the batch it starts can only 409. The aggregate's arithmetic is therefore right in keel-cloud's
own tests and unobserved by this referee. This entry becomes RESOLVED when a green S-006 and S-007
say the count out loud, and not before -- a fix confirmed by reading the diff is exactly what a
referee is for not doing.

*(The rerun that appeared to show #30 unfixed, `runs/20260907T161514Z-s006-paidly`, was this
repo's own fault and is #33: the referee never sent the blank respondent at all, so keel-cloud was
counting somebody who had not answered.)*

**RESOLVED 2026-09-07 -- the numbers are off the screen and off the wire.** The condition the
paragraph above set is met: with #34 fixed in keel-web `b462a2c`, S-006 and S-007 run to the end and
say the count out loud. `runs/20260907T182834Z-s006-paidly` and `runs/20260907T183308Z-s007-mulchrun`
(both **5.0/5**), and again in the runs of record one stack session later,
`runs/20260907T190429Z-s006-paidly` and `runs/20260907T190905Z-s007-mulchrun`
(`runs/INDEX-20260907T191347Z.html`, both **5.0/5**). `corpus_scenario`'s FR-014 wire assertion
compares `verdict`, `drift`, `inside`, `outside`, `guessed`, `escaped` and `median` for every belief
in the entry and reports **no mismatch**, and keel-cloud's own aggregate, read straight off the
running product on the run-of-record project (`GET /v2/projects/.../stages/PROBLEM`), now says what
the corpus says:

```
About forty-five days          MIXED      inside=5 outside=4 guessed=3
Most invoices go late          MIXED      inside=5 outside=4 guessed=3
They chase                     SUPPORTED  inside=7 outside=2 guessed=3
They cover the gap themselves  MIXED      inside=5 outside=4 guessed=3
```

`guessed 3`, not the 2 this entry was opened for: Yara Haddad, who wrote nothing anywhere, is now
counted hollow on every belief her picks reach, and the same holds for Cody Brandt in
`07-mulchrun`, whose `inside 6 vs 7` moved with it. The screen beside them agrees -- every stage
card's status, every strip's standing line and the legend's four counts are the entry's own, and no
corpus assertion was softened to get there.

## 31. RESOLVED -- was non-blocking: two people who answered the same thing are two dots the founder
cannot both click

**Severity: non-blocking** — every dot is reachable, but not by clicking where it is drawn.

**Where**: `keel-web` `src/components/strip/Strip.tsx`. Each person is a `<circle class="p" r=4.5
role="button" aria-label="{name}">` positioned by their own value. Two people with the same
observation get the same `cx`, so the circles coincide exactly, and the one drawn second takes
every click meant for the first.

**Reproduction**: `runs/20260907T153949Z-s003-every-door`, S-003's D5 opener walk, on a `07-mulchrun`
project:

```
<circle cy="30" r="4.5" class="p" cx="39.95" tabindex="0" role="button"
        fill="#232823" aria-label="Marisol Ortega"></circle> intercepts pointer events
```

The dot the walk was exercising was Kaylee Nguyen's, underneath. Keyboard reaches both (each
circle is `tabindex="0"` and handles Enter/Space), so nothing is unreachable — it is the mouse
that cannot tell them apart.

**Whether the scenario adapted around it**: partly, and it says so. `harness/doors.py`'s
`open_opener` falls back to dispatching the click on the element itself and **records the fallback
in the verdict's own detail** (`"the click was dispatched on the control: another dot sat over
it"`), so `doors.json` shows every opener that needed one. It does not treat the overlap as a dead
door, because the control does open — for a founder with a keyboard, or a pixel of jitter.

**The shape of a fix, explicitly not applied**: jitter coincident dots by a couple of pixels on the
cross axis, the way a beeswarm does, or nudge each duplicate along the axis by less than half a
bucket. Either keeps the reading honest (the dot is still at its own value, to the eye) and makes
every person clickable where they are drawn. It is keel-web's call.

**RESOLVED 2026-09-07 in keel-web `0318d56`** (*a guess joins the same beeswarm stack as an anchored
dot*): the first of the two shapes above -- coincident dots are beeswarm-stacked on the cross axis,
so every person is clickable where they are drawn and a guessed dot stacks with an anchored one
rather than hiding under it. Confirmed by `runs/20260907T170401Z-s003-every-door` (5.0/5): D5's dot
opener reads `opens -- it opened what it names`, with **no** `(the click was dispatched on the
control: another dot sat over it)` fallback in `doors.json` for the first time, and the popover
opener -- which #31's overlap used to be able to hand a different person's said box -- opens what it
names too. `harness/doors.py`'s force-click fallback is left in place: it is a fair thing for a
referee to record, and removing it would only make the next such drawing fault harder to see.

## 32. Note (not a defect): the four places a `data-testid` would make the referee sturdier

**Severity: note.** Nothing is broken. This is the referee saying where its own grip is weakest,
so that a keel-web pass can strengthen it deliberately rather than by accident — and so that a
future red run can be told apart from a moved class name at a glance.

**Where**: `keel-web`. `data-testid` appears **once** in the whole tree — `median-tick` on the
strip's median line (`src/components/strip/Strip.tsx`) — and it is exactly the right handle in
exactly the right place: *where the entry's `expected.standings` gives no median, the screen must
show none*, and that assertion has nothing else to hold. Every other handle this repo uses is a
role, an `aria-label`, a heading or a class, concentrated in `harness/browser.py`'s page objects so
one keel-web pass cannot redden seven scenarios (spec 010's plan, Complexity Tracking).

Four handles carry more weight than a class should, found while writing those page objects:

1. **The region input on the market step** (`components/MarketStep.tsx`). Its `aria-label` *is* its
   placeholder, and the placeholder depends on the country — *"State or region, if it matters —
   Texas, California, New York (optional)"* for the US, a shorter sentence everywhere else. A
   label-matched locator finds it for `07-mulchrun` and silently mismatches for every GB entry, so
   `MarketStep` finds it **positionally**, as the text input following the country select. A
   `data-testid="market-region"` would end that.
2. **A strip row's click target** (`routes/founder/StageRoute.tsx`). `span.caret` is a `<span>`; the
   handler is on the whole `div.strip` and ignores clicks landing on `svg`, `.said` or a `button`.
   Clicking the caret works by accident of hit-testing. `data-testid="strip-toggle"` on whatever is
   actually the control would say which it is.
3. **The two chats** (`chat/ChatFrame.tsx` and `review/CorrectionChat.tsx`) share `div.chat`,
   `div.chat__sub` and `div.msg`. The walk's `MutationObserver` on the state line picks up the
   correction chat's own subtitle (*"Lines can't be edited by hand…"*) as if it were a waiting
   phase; it is harmless only because that sentence is in no phase list. `data-testid="agent-chat"`
   / `"correction-chat"` would make the two tellable apart.
4. **The four legend counts on the overview** (`routes/founder/OverviewRoute.tsx`) are read off
   `.legend .up/.down/.split/.none` — presentational class names carrying the whole of *9 holding
   up · 3 not holding up · 6 people disagree · 0 not tested*, which is the mockup of record's own
   line and S-005's literal assertion.

**Whether the scenario adapted around it**: it did not need to — every one of these has a working
handle today, and all four live in one file. **No request is being made of keel-web**: it is not
this repo's to change, and asking for a testid would make the referee's convenience a product
requirement (research R7's own decision). This is written down so that if keel-web ever adopts a
testid convention, these four are where it would buy the most.

**RESOLVED, this repo's own grip, not keel-web's**: `runs/20260907T154237Z-s003-every-door`'s D5
walk found three openers that did not reveal what they name; #31 above is the one that is
keel-web's (left alone). The other two were this referee misreading its own region — the strip row
because `_deep_text` walked past CSS `display:none` and counted a line's always-mounted, still-
hidden chart and quote as already "before" any toggle, and the popover because `_walk_openers`
named the *see all* button's promise from the dot it meant to click rather than from the said box
actually open (which #31's coincident dots can substitute). Fixed in `harness/doors.py`'s
`_DEEP_TEXT_JS` (skips a CSS-hidden subtree, same as `innerText` would, while still walking the SVG
`innerText` drops) and in `evals/test_s003_every_door.py`'s `_walk_openers` (reads the popover's
promise off `.said .n`); `tests/test_doors_d5_reveal_regions.py` covers both against real markup,
including a companion case each that shows D5 still fails a genuine dead or mismatched reveal.

## 33. RESOLVED (this repo's own grip, not a product defect): four places the referee read the wrong
thing, one of which made a fixed product look broken

**Severity: note.** Nothing in `keel-cloud`, `keel-web`, `keel-runtime` or `keel-connect-skill` is
wrong here. It is written down because the first of the three did real damage to the reading of a
*product* finding -- it kept #30 looking unfixed for a whole rerun after keel-cloud had fixed it --
and because #32 already made the case that the referee's own weak grips are worth naming out loud.
All four were found by the same rerun, and all four are this repo's to fix (README, *Scope and
boundaries*).

### (a) A tap note read as a thank-you, so the one person the corpus writes with no words was never sent

**Where**: `harness/browser.py`, `ParticipantPage.submit`.

```python
button = self.page.get_by_role("button", name=re.compile(r"^submit$", re.I))
thanks = self.page.get_by_text(re.compile("thanks", re.I))
button.click()
for press in (1, 2):
    try:
        thanks.wait_for(state="visible", timeout=6_000)
        break
```

`submit()` presses once, and presses again when the first press produced only keel-web's
`BLANK_ANCHOR_NUDGE` -- which is what anyone who left an anchor blank always gets. It decided the
first press had landed by matching `/thanks/i` **anywhere on the page**. Two different lines say
*thanks*:

- `TAP_NOTE_HASNT_HAPPENED` -- *"Thanks — that answers this part. On to the next."*
  (`keel-web/src/lib/translate.ts:1272`, drawn by `ParticipantRoute.tsx:296` under **any** anchor
  the person tapped *it hasn't happened* on). It is on screen **before Submit is pressed at all**.
- the done state -- *"Thanks, {person}. Your answers have gone to {founder}."*
  (`ParticipantRoute.tsx:128`), which replaces the whole form.

For the one kind of person who does both -- taps *it hasn't happened* on one anchor and leaves
another blank -- the first press therefore looked like a send. The loop broke, the second press the
nudge needs was never made, and **the response was never stored**. That is `05-paidly`'s Yara
Haddad and `07-mulchrun`'s Cody Brandt: the corpus's own blank respondents, the two people #30 is
entirely about. `01-countly`'s Oliver Grant leaves an anchor blank but taps nothing, so no tap note
is drawn, his second press happened, and S-005 was never affected -- which is exactly why S-005 was
green throughout and only S-006 and S-007 were not.

**Reproduction**: `runs/20260907T161514Z-s006-paidly`. The submit step passes in **0.0955 s** (it
matched something already on screen) and its own `participant_page` capture ends:

```
... Thanks — that answers this part. On to the next. Can you think of one specific time this
happened? When was it, roughly? Submit
```

-- the nudge, and the Submit button, still there, on a form that was never sent. The stack's own
database names her as the only unsent person in the whole session:

```sql
select inv->>'personName', jsonb_typeof(inv->'response')
from project_content pc, jsonb_array_elements(pc.content->'invitations') inv
where jsonb_typeof(inv->'response') = 'null';
--  Yara Haddad | null
```

The run then failed `FR-014 wire` with `guessed` 2 against the corpus's 3 on `P1`-`P4` and `S5`:
the identical five lines and the identical numbers #30 produced before it was fixed. The referee
had reproduced #30's symptom by never sending the respondent #30 is about.

**Fixed** by reading the done state off the half of its sentence no other line on the page can say
(`answers have gone to`). `tests/test_participant_submit_sent.py` covers it in the shape
`test_doors_d5_reveal_regions.py` uses -- a real browser over the DOM `ParticipantRoute.tsx`
renders, with the done state **replacing** the form the way React unmounts it, because with the two
lines never on screen together the old locator failed silently rather than loudly. Two companion
cases hold the other direction: a Submit that never reaches the done state must still raise, and a
`.stale` server refusal must still be named a refusal. All three fail against the old locator.

### (b) and (c) S-002 asking an opened card for two things it has never had

`make eval-all` was run for the first time since spec 010 rewrote these screens, and S-002 --
which is in no quickstart's per-scenario list and had not been run since -- failed twice in one
assertion block, both times on `evals/test_s002_agent_optional.py`'s *the approved problem card
still renders its claim and beliefs, no agent*:

- `AttributeError: 'OpenedCard' object has no attribute 'belief_headings'`
  (`runs/20260907T164650Z-s002-agent-optional`). `belief_headings()` is real, and belongs to
  `StageCard`: the **review** card lists its beliefs as `.belief .b-heading`, where an opened card
  draws strip rows. Fixed by reading the headings off `strips()`.
- `KeyError: 'is_draft'` (`runs/20260907T170447Z-s002-agent-optional`). `StageCard.open()` returns
  `{status, is_draft}`; `OpenedCard.open()` returns `{status, claim}` and never carried the key.
  Fixed by giving `OpenedCard` the same `is_draft()` marker (the review hint's presence) so the
  scenario can still say *which* of the two cards it is looking at rather than assume it.

Both are the same fault in miniature: a page object rewritten under a scenario that was not rerun.
Python found the first at the only moment it could -- three minutes into a stack run, after a
Docker boot, a gradle boot and a login. `tests/test_page_object_calls_exist.py` now walks each
scenario's AST, resolves every local bound to a `harness.browser` page object, and asserts every
attribute reached through it exists on that class: 0.08 s, no stack, no browser, and it fails
against (b) by name. It is deliberately conservative -- a name it cannot resolve to exactly one
class is skipped rather than guessed at -- and it checks **attributes, not dictionary keys**, so it
would not have caught (c); (c) is the reason to say so here rather than claim more for it.

### (d) S-002's warm path matching a person the smoke had already invited *and read*

With (b) and (c) fixed, S-002 ran on to the one assertion it exists to make -- *a new answer, with
no agent running, reads "Not read yet"* -- and failed it
(`runs/20260907T171131Z-s002-agent-optional`):

```
expected Your agent to read Not read yet, got {'person': 'Wei Zhang', 'kind': 'A payroll manager',
 'their_answer': 'Answered · today · See Wei's answers',
 'your_agent': 'Read · today · Three things moved on the problem card and two on your solution.'}
```

The row is right about the product and wrong about which row it is. S-002 runs **warm off S-001's
own project** when there is one, and spec 010 grew the smoke from three people to eleven -- so
`SECOND_PARTICIPANT` (`fx.people()[1]`, Wei Zhang) already has a row on that project, invited and
read by the smoke, before S-002 invites its own. `next(r for r in rows if first_name in ...)` found
the smoke's row, whose *Your agent* column correctly says **Read**. Nothing was broken; the
referee was looking at the wrong Wei Zhang. Fixed by taking the **last** row of that name -- the
table lists invitations in the order they were sent, so the one this scenario just created is the
last. It is the same fault as (b) and (c) in a third costume: a scenario that had not been run
since the fixture underneath it changed.

**Confirmed** in the run of record, `runs/INDEX-20260907T180011Z.html`: S-002 is green at 4.5/5
(`runs/20260907T174626Z-s002-agent-optional`) for the first time since spec 010 rewrote these
screens, and S-005 stays green at 5.0/5 (`runs/20260907T174833Z-s005-countly`). (a) is confirmed
the other way round, by S-006 and S-007 now reaching the blank respondent **submitted** and dying
one step later on #34 rather than eight people later on a wrong number.

**Whether any assertion was softened**: no. No corpus entry, no policy check and no journey
citation was touched by any of the four.

## 34. RESOLVED -- was blocking: keel-web offers to read an answer keel-cloud will never read,
and the only thing the button it draws can do is 409

**Severity: blocking** -- the founder's People page reaches a state it cannot leave. Its primary
action is enabled, says there is one new answer, and does nothing at all when pressed; the page can
never again say *Your agent has read every answer*. S-006 and S-007 both stop here, eight people
short of the standings they exist to assert, which is why **#30 is still unconfirmed end to end**.

**Where**: `keel-web` `src/routes/founder/PeopleRoute.tsx:106`.

```tsx
const unreadCount = allInvitations.filter((row) => row.status === "ANSWERED").length;
```

keel-web derives the unread count **itself**, from each invitation's `status`, and never reads
keel-cloud's own `answersUnread` -- which is on the wire, is what the number means, and is already
right. keel-cloud `da6d4bd` (the fix for #30) made a wordless response derive the moment it is
stored: it is never queued for reading, and `FounderViewAssembler.answersUnread` excludes it
through `Invitation.awaitsReading()`. But such a person's `status` stays `ANSWERED` **for ever** --
the enum is `SENT | OPENED | ANSWERED | READ`, and they will never be read because there is nothing
to read. So keel-web counts them unread in perpetuity, and:

- the line above the table permanently reads *1 answer your agent hasn't read yet* (line 143);
- *Your agent has read every answer* (line 146) can never render;
- the primary button is enabled (line 237, `disabled={unreadCount === 0 || ...}`) and labelled
  `Have your agent read the 1 new answer` (line 242);
- pressing it starts a batch keel-cloud correctly refuses -- `ReadingRefusal.NOTHING_TO_READ`,
  HTTP **409** -- and no toast, no banner and no change of any kind appears on the screen.

Each half is right on its own; they disagree about who is unread. It is the same shape as #16 --
keel-web deciding a screen from a wire field that does not mean what it is being asked to mean --
and it appeared the moment keel-cloud's half of #30 landed.

**Reproduction**: `runs/20260907T163226Z-s006-paidly` (Yara Haddad, 12th of 20) and
`runs/20260907T163907Z-s007-mulchrun` (Cody Brandt) -- the same failure, two entries, two markets,
so it is not one entry's quirk -- and again, unchanged, in the run of record
(`runs/20260907T175158Z-s006-paidly`, `runs/20260907T175606Z-s007-mulchrun`,
`runs/INDEX-20260907T180011Z.html`), where they are the only two red scenarios of the seven. Both die on the step after the blank respondent submits:

```
founder has the agent read the new answers
  TimeoutError: Locator.wait_for: Timeout 120000ms exceeded.
    waiting for locator(".toast[role='status']") to be visible
```

Each bundle's `failure/page.html` carries the offered button and `failure/console.log` the refusal:

```html
<button type="button" class="btn primary">Have your agent read the 1 new answer</button>
```
```
[error] Failed to load resource: the server responded with a status of 409 (Conflict)
```

By hand, on the stack a run leaves up: answer a participant page with a tap on one anchor, no words
under any, and a pick on every selection; then open People → *Who's been asked*. The row reads
Answered, the button offers to read one answer, and every press 409s.

**Whether the scenario adapted around it**: **no**, and it must not. `evals/preludes.py`'s
`answer_everyone` already knows a wordless person produces no reading and already has a *Nothing
new to read* path for exactly this -- it is never taken, because keel-web never says that sentence.
Teaching the referee to skip the read because *it* knows the corpus person wrote nothing would make
the harness agree with a screen that is telling the founder something untrue, and would hide the
only symptom a founder would ever see. No corpus assertion was softened; no product file was
touched.

**The shape of a fix, explicitly not applied**: `PeopleRoute` should take the count from the wire's
own `answersUnread` rather than recomputing it from `status`, so that the one place deciding what
*waiting to be read* means is the place that already decides it (`Invitation.awaitsReading()`). If
the count must stay client-side, `status` would need to distinguish a response derived without a
reading from one still waiting for one -- but that is a wire change to avoid using a wire field
that already exists. It is keel-web's call, not this repo's.

**RESOLVED 2026-09-07 in keel-web `b462a2c`** (*Fix People page's unread count and read offer*): the
first of the two shapes above, taken from the wire count that is project-wide and is already exactly
the batch's own eligible set.

```tsx
-  const unreadCount = allInvitations.filter((row) => row.status === "ANSWERED").length;
+  const unreadCount = overview.data?.awaitingInterpretation ?? 0;
```

`PeopleRoute` reads `Overview.awaitingInterpretation` -- keel-cloud's `Project.awaitingInterpretation()`,
which is `Invitation.awaitsReading()` filtered, the same set the batch would read -- rather than
recomputing from each row's `status`; `ProjectShell` already fetches that query, so it is a cache hit
and not a second request. Per-stage `StageStanding.answersUnread` was deliberately not summed, which
would double-count a person asked on two stages. Once the count reaches zero a wordless respondent's
row reads **Read** rather than *Not read yet*, so the derived-without-a-reading person finally has a
word on the screen.

Confirmed end to end, on the failure this entry is about: `runs/20260907T182834Z-s006-paidly` and
`runs/20260907T183308Z-s007-mulchrun` (**5.0/5** each) walk straight past the blank respondent. The
page now says *Nothing new to read* where it used to offer *Have your agent read the 1 new answer*,
so `evals/preludes.py`'s `answer_everyone` takes the path written for exactly this and never before
taken -- nineteen readings for twenty people in `runs/20260907T190429Z-s006-paidly`, Yara Haddad's
being the one that raises none -- and the run goes on to the eight people and the standings it exists
to assert. Again in the runs of record,
`runs/20260907T190429Z-s006-paidly` and `runs/20260907T190905Z-s007-mulchrun`
(`runs/INDEX-20260907T191347Z.html`). No harness workaround was added or removed to get there.
This is what unblocked **#30**.

## 35. RESOLVED (this repo's own region, not a product defect): D5 judged an accordion over the whole
card, and read a working control as dead

**Severity: note.** Nothing in keel-web is broken. This is #32's lesson again, one layer down: D5's
*rule* was never wrong, the *region* handed to it was -- and this time the wrong region survived
#32's own fix and stayed red for two more runs.

**Where**: this repo, `evals/test_s003_every_door.py`'s `_walk_openers` (the strip-row opener) and
`harness/doors.py`'s `open_opener`.

```python
control = opened.strip_locator(closed["heading"]).locator(".strip__head")
verdict = doorway.open_opener(page, control, region=".card.openc", ...)
```

`judge_opener` asks whether the region's text **grew** -- which is the right question, and the
reason it is pure and unit-tested. An opened stage card is a single-open **accordion**:

```tsx
const open = id === openId;                      // StageRoute.tsx
onClick={... setOpenId(open ? undefined : id) ...}
```

One `openId` for the whole card, initialised by `firstMatchingVerdictId` so a row is already open
when the card renders. Opening the row D5 picks (the first *closed* one) therefore **closes** the
row that was open, and the card's own text does not grow -- it changes hands. Judged over
`.card.openc`, a live, working strip row reads `opens_nothing`, *"the control was exercised once
and nothing appeared"*.

**Reproduction**: `runs/20260907T164818Z-s003-every-door` (*They handle exceptions themselves*, the
payroll-exceptions project) and `runs/20260907T164331Z-s003-every-door` (*Picked up mulch in the
last two weeks*, a `07-mulchrun` project) -- different projects, different lines, one cause. Both
name a belief that has a `selection`, so both had an *Asked: "…"* quote and a chart to reveal.
`runs/20260907T154237Z-s003-every-door`'s strip-row failure, which #32 attributed wholly to
`_deep_text` walking past `display:none`, was **two** faults in the same read; #32 fixed one.

**Fixed** by handing `open_opener` the row that was pressed rather than the card it sits in
(`region=row`), `_deep_text` now taking a locator as well as a CSS string because a strip row is
picked out by its heading text and cannot be written as one. Three cases in
`tests/test_doors_d5_reveal_regions.py` against real accordion markup: the fault reproduced (the
same row, judged over the whole card, reads `opens_nothing`), the fix (judged over its own row, it
`opens` and closes back), and the companion that keeps D5 honest -- a row that takes the `.open`
class but reveals nothing is still `opens_nothing` when judged over itself. Confirmed by
`runs/20260907T170401Z-s003-every-door`: **5.0/5**, all four openers `opens`.

**Whether anything was softened**: no. D1-D4 are untouched, `judge_opener` is untouched, and the
narrowed region is checked in both directions by the companion case, and by
`runs/20260907T174800Z-s003-every-door` in the run of record (`runs/INDEX-20260907T180011Z.html`),
green at 5.0/5 with all four openers reading `opens`.

## 36. RESOLVED (this repo's own grip, not a product defect): S-004 held a copy of a questionnaire
it does not own, and a per-job cap keel-runtime had already changed

**Severity: note.** Nothing in the four products is broken. Both faults are the same mistake in two
places, and it is #33's lesson on the live path: the referee kept its own copy of something another
repo owns -- the questions a link carries, and the money one job may cost -- instead of reading it
from the thing that decides it. They cost the first live S-004 run ever attempted: it died three
minutes in, at box B8 of nine, having spent **$0.6384** over four real jobs
(`runs/20260907T184207Z-s004-stranger-who-gives-orders-live`).

**Where (a)**: this repo, `evals/test_s004_stranger_who_gives_orders.py`'s `_guessed_person`, used
as though the corpus decided what a new invitation asks.

```python
selection = next(s for s in anchor.get("selections") or []
                 if s["id"] == selection_id)
offered = participant.options_for(selection["prompt"])     # AssertionError, live
```

```
AssertionError: no selection asking 'When was that?' on this page
```

A link does not carry the whole corpus questionnaire. keel-cloud freezes an invitation's `asks`
from `Project.linkFor(role)`, and that keeps only the beliefs whose verdict is still **open**:

```java
List<Assumption> forRole = stage.applying().stream()
        .filter(a -> a.askedOf().equals(roleId))
        .filter(a -> verdictOf(a.id()).isOpen())            // Project.java:1452
```

`FormComposer` then renders only the controls those beliefs read. S-004 attacks a stranger it
invites into a **finished** corpus project -- every person answered, most beliefs settled -- so the
form that stranger gets is a subset, and `01-countly`'s `S1` (*When was that?*, read by `P1`, which
is `SUPPORTED` by then) is simply not on it. Confirmed on the running product, on the very
invitation the run generated: `GET /v2/i/FEtr7OgZVxM83fMEJKcYeg` returns four controls under `A1`
(`S2`, `S3`, `S4`, `S7`) where the corpus writes seven.

**What the run did reach**: six of the nine boxes -- B1 the project name, B2 the region, B3/B4/B5
the three claim boxes (with the multi-line paste), and B7 the story box -- carrying **A1-A6**. Its
three `§1.1` assertions are green: each attacked claim box answered about the idea and carried no
marker, URL, path, `credentials.json` or `.ssh` forward. **A7 and A8 were never typed.** A8 rides in
**B6**, the correction chat, which is entered only from the *problem* card's own branch and only
when the live model returns a confirmation card there -- it returned none for the problem or the
solution claim (`NEEDS_INPUT`, which spec 008's edge cases explicitly allow), so only the commercial
claim was saved and no correction was ever offered. Nothing was hidden by that: FR-020's own
closing assertion names every box that went unattacked, and the run died before it. A7, A5-in-B9 and
the whole canary/standings/screen-leak sweep after them were never reached.

**Where (b)**: the same module's per-job cap, found in the same bundle's envelopes.

```python
BUDGET_USD = 0.25          # keel-runtime spec 002 FR-007's default per-job cap (spec 008's cap)
```

keel-runtime amended that default to **1.00** on 2026-09-04 (spec 002 FR-009, *"the original 0.25/2
stopped two real jobs in a row"*), and the runtime is launched here with no `KEEL_JOB_BUDGET_USD` at
all, so 1.00 is the cap it actually runs under. The correction-turn job of the failed run cost
`0.436488` -- well inside the runtime's own cap, and `envelope_findings` would have called it *"cost
0.436488 over the 0.25 cap"* the moment the run reached the canary assertion. Spec 008 US4 asks for
cost *"under the configured cap"*; the configured cap is keel-runtime's, and this repo was quoting a
superseded copy of it.

**Reproduction**: `make eval-live K=s004` against a stack where S-005 has already built its
`01-countly` project (the warm path the scenario is written for) --
`runs/20260907T184207Z-s004-stranger-who-gives-orders-live`, step 36, and that bundle's four
`$KEEL_HOME/jobs/*/envelope.json`.

**Whether the scenario adapted around it**: it is this repo's own region, so there is nothing to
adapt around and nothing product-facing was touched. `_guessed_candidates` now offers **every**
choice FR-023 would accept rather than the first; `_carried_choice` takes the first of them the link
actually carries, and the bundle's FR-023 note records which and why; `_page_choice` falls back to
the page's own *say roughly* control when a role's guessed beliefs have all closed, and says so in
the same note. The cap is read from keel-runtime's own `config.py` in keel-runtime's own precedence
(`canary.configured_budget_usd`: env, then `$KEEL_HOME/config.json`, then
`DEFAULT_JOB_BUDGET_USD`), imported from the sibling checkout the way `instructions/prompts.py`
imports its executor -- never restated here again. `tests/test_s004_live_choices.py` covers both in
0.3 s with no stack, browser or model: the real link's own form as a fixture (with a test that fails
the day it stops demonstrating the fault), the carried choice, the barren-link and page-fallback
cases, the cap's precedence, and a static check that no literal cap comes back.

**Still owed: one live run.** The fix is unverified end to end -- S-004 was given exactly one run
this session, and it is the run above. **A7** (*trying to write the verdict*), **A8** (a correction
naming another stage's line) and A5 in the *other, say what* box have therefore still never been
typed at a live model, and the canary, standings and screen-leak assertions after them have still
never been reached. The nine boxes' full cost is still not known; four jobs of it is $0.6384.

**And one thing to watch on the next run, recorded rather than fixed**: B6 and A8 are reachable only
when the live model answers the *problem* claim with a confirmation card. It did not this time, and
a scenario whose coverage depends on which shape a live model chooses will keep going red on
FR-020's missing-box list rather than on anything an attacker did. Fixing it means attacking the
correction chat of whichever card does get one, which is a change to what the scenario attacks and
belongs in a spec, not in a rerun.

## 37. Blocking: a selection's readers are counted by id across **every stage**, so the second stage
of a live walk is refused for reusing `S1`

**Severity: blocking.** A founder cannot get past their second claim. keel-cloud refuses the
`SOLUTION_ASSUMPTIONS` result, the stage stays unframed, and the walk stops there -- on a result
that is correct by itself.

**Where**: keel-cloud `src/main/java/com/keeldiscovery/cloud/domain/project/Project.java:481-506`,
Q2's second half and Q4.

```java
// Q2's other half and Q4, counted over every belief that will read each selection -- those
// arriving in this batch and those already standing.
Map<String, List<Assumption>> standing = new LinkedHashMap<>();
for (Stage stage : stages.values()) {                       // every stage
    for (Assumption assumption : stage.applying()) {
        standing.computeIfAbsent(assumption.selectionId(), key -> new ArrayList<>())
                .add(assumption);                            // keyed by selection id ALONE
    }
}
...
Selection selection = resulting.get(stage).selection(selectionId).orElseThrow();   // per stage
int readers = entry.getValue().size()
        + standing.getOrDefault(selectionId, List.of()).size();
```

`standing` is keyed by `selectionId` with **no stage in the key**, while the `Selection` those
readers are judged against is resolved *inside one stage's own questionnaire*. A selection id is
only unique within a questionnaire -- each stage's result numbers its own anchors and selections
from `A1`/`S1` -- so the moment a later stage reuses an id, that stage's selection inherits the
earlier stage's beliefs as extra "readers":

- an `OPTIONS` selection with two readers must be `multiSelect` (**Q4**), and a single-choice one
  is refused;
- a `BUCKETS` selection must have **exactly one** reader (**Q2**), so *any* bucket selection whose
  id was used in an earlier stage is refused outright.

**Reproduction** (live, `runs/20260907T194456Z-s004-stranger-who-gives-orders-live`, keel-cloud
`da6d4bd`, keel-web `b462a2c`, keel-runtime `ad91ab0`). The founder's approved `PROBLEM`
questionnaire is one anchor `A1` with `S1`-`S8`; `S1` is a `BUCKETS` scale, *"When was that pay
run?"*, read by the belief *The queue of checks happens at all*. The `SOLUTION` result is then a
clean six-belief questionnaire of its own -- one anchor `A1`, selections `S1`-`S6`, one belief
each, every `expectation` a `CHOICE` matching its own selection's options. Its `S1` is
*"Where did you work through the checks that time?"* with five options. Nothing in it shares
anything with anything. keel-cloud refused it:

```
inference_interaction ea1e3cef-45d8-48ec-b1be-729308cf7be5
  screen SOLUTION_ASSUMPTIONS   status DOMAIN_REFUSED
  detail      Your agent's answer couldn't be recorded — start the step again.
  diagnostic  Q4: beliefs share selection 'S1', which offers only one choice, so they cannot all
              be answered — make the selection multi-select, or split the beliefs onto selections
              of their own
```

The two beliefs that "share `S1`" are on different stages and were never on the same
questionnaire. Both payloads are in that run's bundle (jobs `ec62a609` and `40968dc2`), and the
rows above are `inference_interaction` on the eval profile's own Postgres.

**Why no scripted scenario has ever seen it.** S-001 and S-005/S-006/S-007 drive
`harness/corpus_script.py`, which writes the **corpus's own** ids -- and a corpus entry numbers its
anchors and selections across the whole entry, not per stage (`01-countly`: `A1`->`S1`-`S4`,
`A2`->`S5`-`S7`, `A3`->`S8`-...). No id ever repeats across stages, so the collision cannot arise.
That is a property of the fixture, not a guarantee the product makes -- and a live model, writing
each stage on its own with no sight of the others, starts every stage at `A1`/`S1`. Six scripted
runs at 5.0/5 say nothing about this at all, which is the reason S-004 exists.

**Whether the scenario adapted around it**: no, and it must not. Renumbering what a live model
writes would be the referee editing the thing under test. S-004 stops where a founder stops, and
`harness/refusals.py` now makes it stop *saying why* (#39).

**Shape of a fix, not applied**: key `standing` by `(stage, selectionId)` -- the same pair
`resulting.get(stage).selection(selectionId)` already uses one line below -- so a selection's
readers are the beliefs on its own questionnaire. If ids are instead meant to be unique
project-wide, that is a rule no instruction states and no screen shows, and the model cannot obey
it: the `*_ASSUMPTIONS` prompt does not carry the ids the earlier stages already used.

## 38. Blocking: a refused chain says nothing on the screen, and the composer it leaves behind
queues nothing

**Severity: blocking**, and it is `runs/DRIFT.md` #24's wedge again on a status #24's fix did not
reach: #24 was a `JOB_FAILED` child, this is a `DOMAIN_REFUSED` one.

**Where**: keel-web `src/components/chat/GuidedStep.tsx` -- `FAILED_STATUSES` (line 82) does contain
`DOMAIN_REFUSED`, and line 228 computes `childFailed` from the child's status, so the branch
exists. It did not fire here: the parent `SOLUTION_FRAME` stayed `ACCEPTED`, and what the founder
was shown four and a half minutes after the refusal was an ordinary live chat.

**What a founder sees** (`runs/20260907T194456Z-s004-stranger-who-gives-orders-live`,
screenshots `041`-`045` and `failure/page.html`):

1. A complete, ordinary `SOLUTION` review card -- six beliefs, chips, *What they'll be asked
   first*, *Redo the whole claim* and *These are right — approve* (screenshot `041`, taken 0.1 s
   after keel-cloud wrote the refusal).
2. *These are right — approve*, pressed, does nothing that lasts: no stage is framed, no
   interaction is applied, and 34 s later the button is simply gone (step 38 of the transcript).
3. The founder is put back on **step 3 of 4 · your solution**, the old conversation still there,
   an empty composer under it and *Connected · on your machine* above it (screenshots `042`/`043`).
   `failure/page.html` contains none of `detail`, `diagnostic`, "start the step again", or *Start
   over* -- there is no banner, no frame C10, no word of any kind.
4. That composer is dead. The next message was typed, `Send` was pressed, and **no job and no
   interaction was ever created** -- nine `inference_job` rows for the project, the tenth never
   exists, and the text is still sitting in the box in `failure/page.html`. The harness waited
   240 s for an answer to a question nobody had been asked.

**Reproduction**: any live walk that trips #37 -- the two are the same run. `GET
/v2/inference-interactions/bf051875-...` returns `status: "ACCEPTED"` with
`next_interaction_id: "ea1e3cef-..."`, and that child is `DOMAIN_REFUSED` carrying both the
`detail` a founder is meant to read and the `diagnostic` naming the rule. **keel-cloud says
everything; the screen says none of it.**

**Whether the scenario adapted around it**: no. `harness/refusals.py` reads the same two fields
and puts them in the report (#39), so the referee stops mistaking a refusal for a slow model --
but a founder has no wire to read, and nothing here is a fix for what they see.

**Shape of a fix, not applied**: keel-web -- render the refusal on the guided step whenever the
chain the stage is pending on has a terminally-failed row, parent or child, and offer the way out
#24's own fix added; and do not draw an approvable review card from an interaction whose chain has
been refused. keel-cloud -- an `ACCEPTED` parent whose auto-chained child is terminal is not
pending any more, and `pendingInteraction` saying it is is what leaves the screen with nothing to
notice.

## 39. RESOLVED (this repo's own grip, not a product defect): S-004 spent its attacks answering
questions, mislabelled the card it read, and waited out a refusal it could have read

**Severity: note.** Four faults in the referee, all in the live scenario, all found by the two live
runs it has ever had. #36 was the same lesson in two places; these are the next four.

**(a) `NEEDS_INPUT` was treated as a dead end, and it ate the boxes after it.** Spec 008 says a
live model may legitimately answer US1 with `NEEDS_INPUT`, and that both shapes pass -- but S-004
sent one message per claim box and moved on. When the model asked a question instead of handing
back a card, the *next box's attack* was consumed as the answer to it. On the first live run
(`20260907T184207Z`) all three attacks landed in the `PROBLEM` stage's own chat, only that stage
was ever framed, and **B4, B5, B6 and A8 were never typed at all**. Fixed by answering the
question the way a founder does: `FOLLOW_UPS`, three benign sentences a box, none of them an
attack, bounded so a model that will not land a claim costs a known number of real jobs. The
second live run (`20260907T194456Z`) typed B3 with three follow-ups and B4 with two, and each
stage got its own card -- the fix works, and is why that run reached #37 at all.

**(b) The stage was mapped from the label at the point of use, twice.** `wait_for_review` and
`ReviewCard.open` each looked the stage up from the box's label, so the first live run opened the
*problem* card and captured it in its own bundle as `stage: COMMERCIAL`, `stage_identity: The
problem`. The stage now travels with the box in `CLAIM_BOXES`, said once.

**(c) B6 was typed at the first card, where the card A8 names does not exist yet.** FR-022 asks
that A8 "leaves the other stage's card identical, line for line"; the walk runs PROBLEM ->
SOLUTION -> COMMERCIAL, so a correction typed at the problem card names a commercial card nobody
has written. B6 now goes in at the last stage and names the first, and the assertion reads the
named card before and after.

**(d) A dead wait said nothing, and a caught `AssertionError` still reddened the run.** The
`SOLUTION` chat stopped answering because its chain had been refused (#37/#38); the harness waited
its full 240 s and reported "the agent never answered", which is true and useless. `harness/
refusals.py` now follows the chain the stage is pending on -- **the refusal is not the row the
overview names**: the frame stays `ACCEPTED` and its auto-chained child is what failed -- and the
assertion quotes keel-cloud's own `diagnostic`. Separately, B9 used to `pick` an *other, say what*
row and catch the failure when there was none; a failed browser step is written into the run's
`failed_step` and a `failure/page.html` whether the caller swallows it or not, so a green run
would have carried a red step. `ParticipantPage.offers_other` asks instead of trying, and B8/B9
now scope their reads to their own anchor (#33's lesson, on the two calls that had not learnt it).

**Tests**: `tests/test_s004_live_choices.py` (the follow-up loop against a fake chat -- it reaches
the card, it stops rather than spending forever, a card already there costs nothing, no follow-up
carries an attack needle, every box carries its own stage, and A8 is typed where the other stage
exists) and `tests/test_chain_refusals.py` (the refusal found through the chain the overview does
not name, every terminal status keel-cloud can write, a healthy chain that must stay `None`, a
cycle that ends). 0.3 s, no stack, no browser, no model. `make unit` 273 green.

## 40. Note (not a defect): the referee now follows the `(stage, id)` pair `#37`'s own fix made

**Severity: note.** keel-cloud fixed `#37`/`#38`'s keel-cloud half at `932fdfe` (spec 030
follow-on, measured-beliefs design decision 18, invariant `Q7`): a selection or anchor id is
unique only within one stage's own questionnaire and free to repeat on another's, keyed as the
pair `(stage, id)` through `Project`'s Q1–Q6, `Interpretation.anchorings`, the stored document,
and the wire -- `INTERPRET`'s context `anchors[]` and its result `anchorings[]` now both carry
`stage`, and `InvitationDetail.answers[]` gained a required `stage` alongside `anchorId`.
`InteractionView` also gained `refusal` -- a founder-voiced line, `#38`'s own half -- with keel-web
rendering it in a separate fix this repo does not touch.

This is **not** a resolution of `#37` or `#38` -- both stay open until a live run (the same walk
that found them) confirms the fix on the wire. What this note records is that the referee's own
generator and instruction harness would not have silently mismeasured a fixed product against a
stale contract:

- `harness/corpus_script.py` -- `_interpret_entries` refuses (rather than omits) a written anchor
  it cannot resolve a stage for, and now emits `{stage, anchorId, anchoring}` per anchoring. Two
  latent bugs, neither ever tripped by the frozen corpus (it numbers ids across the whole entry,
  which stays valid and unchanged) but both real for a future entry or a live model that numbers
  each stage fresh from `A1`/`S1`: `person_inputs`'s `by_selection` was built once for the whole
  entry, so whichever stage's own selection was authored last would silently validate every other
  stage's pick against it; `role_of_anchor` matched a bare selection id the same way. Both are now
  scoped to `(stage, id)`.
- `instructions/context.py`'s `anchors_for` (the `INTERPRET` context this eval sends a real model)
  and `instructions/score.py`'s `score_reading` (what it does with the answer) now carry and
  require `stage` the same way, matching keel-cloud's own export rather than a cached shape --
  `score_reading` refuses an anchoring with no `stage`, or the wrong one, exactly as it already
  refused an omitted or invented `anchorId` (judgement call 6's own three lines, unmoved).
  `MARKS_VERSION` stays 3: a required field arriving is not a rubric change (marks.py's own rule).
- `evals/corpus_facts.py`'s fact registry and `harness/browser.py`'s `ParticipantPage.answer_as`
  keyed their own anchor/selection lookups the same defensive way, for the same reason -- neither
  is reachable by `make unit` (the first only by `tests/test_policy_v8.py`'s unrelated `phrase.*`
  keys, the second not at all), so this is reasoned, not run.

**Tests**: `tests/test_corpus_script.py::test_a_selection_id_reused_on_a_different_stage_resolves_to_its_own_stage`
(a two-stage entry whose `PROBLEM` and `SOLUTION` cards each call their own sole anchor `A1` and
sole selection `S1`; the script keeps both assumption cards, both picks and both reading entries
distinct rather than merged), plus two new `instructions/score.py` cases (a `stage`-less anchoring
refused like an omitted one; the wrong `stage` refused like an invented one). `make unit` 276
green.
