# Drift and bugs found by S-001 and S-002

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

## 17. BLOCKING (spec 006-agent-optional's own stated prediction, confirmed): the read action is
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

## 18. Non-blocking: a reading batch's completion toast reappears on every later visit to People,
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

## 19. Non-blocking (worked around: log out and back in): a runtime that reconnects using its own
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
