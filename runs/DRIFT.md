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
