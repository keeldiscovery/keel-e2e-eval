"""The versioned scoring policy (contracts/policy-contract.md; design §5): every check id,
weight, category weight, normalization rule, clarity token list, and waiver lives here. Nothing
in `harness/rubric.py` decides a weight or a wording rule on its own -- it asks this module.

`POLICY_VERSION` bumps whenever a check, weight, or waiver changes here, because a run's score is
only comparable to another run's under the same policy (data-model.md, FR-006).

Judgement calls made while filling in what the contract leaves to the implementation:

1. **Stage-name enum exemption.** `StageType` (`PROBLEM`/`SOLUTION`/`COMMERCIAL`) is deliberately
   left out of `CLARITY_TOKENS`. keel-web's own founder-facing stage headers are the ALL-CAPS
   phrases "THE PROBLEM" / "YOUR SOLUTION" / "WILL THEY PAY" (`lib/translate.ts` `STAGE_LABEL`) --
   two of the three literally contain the enum spelling as an ordinary English word in the
   product's *correct* copy. Sweeping bare `PROBLEM`/`SOLUTION` would flag that copy, not a leak;
   the other five enum families (`WorkflowState`, `Verdict`, `Need`, `Risk`, handle/action names)
   don't share this collision and are swept as designed.
2. **`instruction.content` is swept anyway, even though keel-cloud's own javadoc calls it "the
   paragraph the executing client alone reads"** (not literally shown to today's no-LLM harness
   founder). The contract names `instruction` explicitly under CLA-A1's "founder-facing text", and
   design §2 treats the conversation card as standing in for what a real agent would voice to the
   founder -- so this policy sweeps it as specified, honestly, rather than narrowing the check to
   avoid a finding. Where that surfaces a real leak, it is a DRIFT.md finding, not a reason to
   soften the check (design §6).

   **Superseded by policy v2, judgement call 3 below** -- kept, struck nowhere, because the
   contract history matters: this is exactly the mismeasurement 003-eval-set's design §2 found and
   re-adjudicated as DRIFT #4 ("policy category error, not product text bug"), not a product leak.

3. **Policy v2 (003-eval-set, design §2): CLA-A1/GUI-A2 sweep `display` only, among the three
   protocol texts.** Re-reading the shipped contract (keel-cloud `ActionSchemas.requirements`,
   `InstructionRegistry`'s own javadoc) alongside v1's own failures showed the mismeasurement:
   `instruction.content` and `requirements` are addressed to the *executing agent* -- methodology
   and payload guidance that legitimately names `CONTRADICTED`, `askedOf`, `goingAhead` -- and the
   founder never receives either raw. The only protocol text actually relayed to the founder is a
   handoff's `display` (what the agent tells them happened / what to do). So, v2:
     - `CLA-A1` and `GUI-A2` are removed from agent-cycle interactions entirely (nothing at that
       interaction type is founder-facing protocol text any more).
     - `GUI-A2` gains a handoff variant (a new companion to the existing handoff `CLA-A1`),
       sweeping `display` for the same clarity violations -- GUIDANCE's "founder-phrased" question
       asked of the one protocol text a founder actually sees.
     - `GUI-A1`'s presence/sentence-shape check on `requirements` is untouched (design §2: "keep
       their presence/sentence-shape checks") -- that check never vocabulary-swept in v1 either.
     - `instruction.content`'s only surviving check stays `ORI-A1` (non-empty, names a purpose) --
       presence, not vocabulary.
   This is the whole reason the twenty v1 failures on S-001 (`CLA-A1`/`GUI-A2`, ten interactions
   each, all agent-cycle) disappear under v2 rather than merely passing: they are no longer checks
   this policy runs on that interaction type at all. A seeded raw enum in a handoff `display`
   fixture still fails both `CLA-A1` and (new) `GUI-A2` -- the UI/participant-page CLA-U1/CLA-U2
   sweeps that would catch real founder-facing leakage are untouched by any of this.

4. **Policy v3 (founder-experience design, keel-cloud commits `8b13d04`/`ff1ed48`): the wire grew
   a founder voice on every commit, not only a handoff, and this policy grows to hold it to its
   own words.** `SubmitResponse` now carries `display` (a founder sentence on *every* commit) and
   `recorded` (a server-authored playback of what that commit created); `StateResponse`'s per-
   stage summary carries `verdictLabel`/`needLabel` beside the machine tokens. Three additions,
   contract-first, no existing check reweighted or removed:

     - **FID -- `recorded` playback fidelity.** A new hop id, `"recorded"`, alongside the existing
       six: an agent-cycle interaction's captured `recorded` JSON is exactly the kind of hop
       `harness/rubric.py`'s generic `_fid_checks` already knows how to sweep (verbatim substring,
       same as every other hop) -- no new check *code*, only a new hop a scenario's facts may
       declare, and `harness/driver.py` capturing it off every successful `submit`.
     - **`ORI-A3`/`GUI-A3`/`CLA-A2` -- the commit `display` itself, checked like a handoff's
       always was.** `ORI-A3` is non-empty (>= 10 chars, mirroring `ORI-H1`). `GUI-A3` is the
       contract's own conditional, literally: "when it points at a screen, contains a resolvable
       URL" -- when a URL is present it must be well-formed (`http(s)://`, the "every door must
       open" rule `harness/browser.py`'s own screen navigation already lives by, extended to a
       *sentence's* URL: `FounderBrowser.follow_display_url` is the scenario-side assertion that
       actually clicks through and asserts render, a live check no transcript sweep alone could
       stand in for); when none is present, there is nothing to fail. (Live-confirmed 2026-08-30:
       an earlier draft of this check also required a guidance verb, mirroring `GUI-H1` -- wrong,
       because a commit's continuation often describes what the *agent* does next ("next, put your
       solution into words too"), not an instruction to the founder, and the draft failed
       legitimate copy across every scenario; dropped.) `CLA-A2` sweeps the same `display` for raw
       enums/field names -- CLA-A1's own recalibration (judgement call 3 above) said this
       vocabulary check follows founder-facing wire text wherever it travels, and `display` now
       travels on every commit, not only a handoff.
     - **`CLA-U3` -- `verdictLabel`/`needLabel` sweep.** Read off the `state` JSON a `ui-visit`
       interaction already stashes (`FounderBrowser._capture_common`'s `get_state` snapshot,
       analysis finding A1's own mechanism, reused rather than re-plumbed): once a stage is
       `approved`, its `verdictLabel` must be present and enum-clean; once its `need` is present
       and not `EVIDENCE` (which `FounderVoice.needLabel` deliberately returns `null` for --
       `verdictLabel` already carries the word at that point), its `needLabel` must be present and
       enum-clean too.

5. **Two more English-word collisions, live-confirmed the same day `CLA-A2`/`CLA-U1` started
   sweeping text they never swept before.** `"roles"` (FounderVoice's own "Your roles are saved.")
   and `"EVIDENCE"` (BriefRoute's own "What the evidence said no to" heading, rendered upper-case
   by CSS) are ordinary English in correct, shipped founder copy that happen to collide with a
   context-handle name and a `Need` token respectively -- the same shape as judgement call 1's
   StageType exemption, for the same reason: sweeping them flags the product's own correct copy,
   not a leak. `_ENGLISH_COLLISION_EXEMPTIONS` below.

6. **Policy v4 (founder-experience round 2 -- keel-cloud commits `cef132c`/`dce04a6`, keel-web
   commits `30787d4..760d0d2`): the arrival read, the locked-section IA, and the pointer-to-agent
   variant each get one new check.** Three additions, additive as every prior bump has been:

   - **`CLA-AR1` -- the arrival read's own greeting.** `keel_get_state`/`GET /v2/agent/state`
     with no project now composes a server-side `display` greeting (`FounderVoice.
     arrivalGreeting`) before the founder does anything else at all. Checked the same way a
     handoff's `display` always has been: non-empty (>= 10 chars, the `ORI-H1`/`ORI-A3`
     threshold) AND free of a raw project id -- a founder greeting names a project, never a
     UUID. This is a new interaction type, `"arrival"` (`harness/driver.py`'s new `arrive()`),
     scored on its own rather than folded into `agent-cycle`/`agent-handoff`, since it is neither
     an action nor a handoff -- a read with no token, no commit, nothing to approve.
   - **`ORI-U3` -- the locked People section carries its own why.** Round 2's side nav (design
     §4 item 6) replaces the flat top nav with three progressive sections; the middle one,
     People, is locked (present, not clickable) until the invite gate opens. Locked is not the
     same as silent: `ORI-U3` requires a founder-worded one-line reason wherever a screen visit's
     side nav renders People locked (`harness/browser.py`'s `_capture_common` captures
     `people_locked`/`locked_people_why` off the nav itself) -- skipped (None), not failed, on a
     visit where People isn't locked (nothing to check) or a pre-round-2 bundle that never
     captured the nav at all.
   - **`GUI-U2` -- the pointer-to-agent sentence is a sentence, not a link.** Round 2's focused
     review (design §4 item 4) teaches the next-step pointer to hand off to the founder's own
     agent once the workflow's next need is agent-side framing ("Now work out your solution with
     your Keel agent.") -- deliberately "a destination that is a sentence, not a link" (no URL,
     no anchor). Checked the same way `GUI-A3` checks a *wire* sentence's door, mirrored onto a
     *screen's* own affordance text: when the affordance names the agent, it must carry no URL --
     the absence is the whole assertion. Skipped (None) on any affordance that isn't a
     pointer-to-agent sentence at all (an ordinary "Waiting for your approval" has nothing to do
     with this check, and is free to carry a real link elsewhere on the same screen, e.g. the
     invite screen's own compose form).

   None of the three loosens or reweights an existing check -- `tests/test_policy_v4.py` seeds a
   failing and a passing fixture for each, the same construction-not-assertion method every prior
   bump used.

7. **Policy v5 (relay-design.md §12 item 5): the chat surface gets its own sweeps.** The relay
   moves the founder-agent conversation into keel-web's ChatPane (relay-design.md §9) -- three
   additions, additive as every prior bump, scored on a new interaction type, `"chat-visit"`
   (`harness/browser.py`'s `ChatPane.read`/`.capture`), never folded into `ui-visit` (the pane's
   own state is orthogonal to whichever screen happens to be open beside it):

   - **`CLA-C1`** -- the same vocabulary/structural sweep every other founder-facing surface gets
     (`clarity_violations`), run over the pane's own rendered turn text (`chat_turns`) and any
     playback table's cell text (`chat_playback_table`) combined -- a raw enum or JSON leak in
     either is exactly the CLARITY violation `CLA-A2`/`CLA-U1` already catch elsewhere, extended
     to the venue the founder now actually reads the conversation in.
   - **`ORI-C1`** -- presence-banner honesty. The design's own words (§5, §9): "connected
     silently (absence of banner); disconnected shows the one command to start the agent." This
     check cross-reads the pane's own rendered claim (`chat_presence_banner` empty vs. non-empty)
     against the relay's own wire truth at the same moment (`chat_presence_state`, `harness/
     browser.py`'s `ChatPane.capture` reading `FounderRelay.presence()` live) -- an absent banner
     while the wire reports `connected: false`, or a shown banner while it reports `connected:
     true`, is a founder-facing lie about whether their agent is there, not merely a missing
     affordance. Skipped (None) when no `chat_presence_state` was captured (a bundle that never
     wired a presence reader into `ChatPane`), the same "don't guess" stance `_need_exists` takes.
   - **`GUI-C1`** -- the every-door-opens rule's chat-surface extension. Every link an agent turn
     carries (`chat_turn_links`, `.chat-turn__text a`'s own `href`s) must be well-formed
     (`http(s)://`) -- `GUI-A3`'s own door check, mirrored onto a chat turn's own links, the same
     way `GUI-U2` mirrored `GUI-A3` onto a screen's own affordance text. The live click-through
     itself (`ChatPane.click_agent_turn_link`) is a scenario assertion, exactly as `GUI-A3`'s own
     docstring says no static sweep can stand in for one -- demonstrated in
     `evals/test_s011_relay.py`. Skipped (None) when no agent turn ever carried a link.

   None of the three reweights or loosens an existing check -- `tests/test_policy_v5.py` (renamed
   from `test_policy_v4.py`, the v3/v4 fixtures kept unstruck per this module's own history
   practice) seeds a failing and a passing fixture for each, the same construction-not-assertion
   method every prior bump used.

8. **Policy v4's second addition: an eighth FID hop, `roles_context`.** S-009 (incremental roles)
   traces a role introduced through the roles-ladder front door -- `harness/driver.py`'s
   `get_context("roles")` capture (`_roles_echo_text`) reflects back every role's own `label`,
   granted alongside both `INTRODUCE_ROLES` and `INTRODUCE_ASSUMPTIONS` (`HandleGrants`). No new
   check code: `roles_context` is a hop like any other to the generic FID engine
   (`harness/rubric.py`'s `_fid_checks`), scoped to `agent-cycle` interactions the same way
   `agent_echo`/`interpret_context`/`recorded` already are.

9. **Policy v6 (spec 005-connect-stack FR-010/FR-011): the agent-protocol half of this policy is
   retired along with the harness that observed it.** keel-skill is archived and every judgement
   now runs through keel-runtime's scripted executor, connected by keel-connect-skill and
   confirmed in keel-web -- there is no more founder-agent HTTP/MCP surface for a check to sweep.
   Removed entirely: `ORI-A1`/`ORI-A2`/`ORI-A3` and `GUI-A1`/`GUI-A2`/`GUI-A3` (agent-cycle),
   `ORI-H1`/`GUI-H1` (agent-handoff), `ORI-R1`/`GUI-R1` (agent-refusal), `CLA-A2` (the commit-
   display vocabulary sweep) -- and, since the relay's own chat surface is retired with it (the
   round-5 "Chat" page object drives keel-web's guided-step composer, an unrelated screen),
   `CLA-C1`/`ORI-C1`/`GUI-C1` and the `chat_turns` FID hop go too (a judgement call: FR-010 names
   the agent-cycle/handoff/refusal families explicitly but not these three by name; they are
   struck here because nothing in the rewritten harness can ever produce a `chat-visit`
   interaction to run them against -- recorded under `## Discovered` in tasks.md). The UI-visit
   checks (`ORI-U*`, `GUI-U*`, `CLA-U1`/`CLA-U2`/`CLA-U3`) and the arrival check (`CLA-AR1`)
   survive unchanged -- they read the screen, which is still exactly how a founder experiences
   this product.

   FID keeps only the hops a screen or the participant survey can actually carry now:
   `stage_screen`, `invite_screen`, `participant_page`, `brief` (all four already `ui_visit`/
   `participant_visit` hops, untouched) -- `agent_echo`, `interpret_context`, `recorded`, and
   `roles_context` are dropped with the wire client that used to capture them. The weight-2 rule
   for verbatim participant speech (judgement call, `fid_weight`'s original comment) moves to
   where that speech is actually captured now: `(kind="answer", hop="participant_page")`, not the
   retired `interpret_context`.

   Three additions, scored on `ui_visit` interactions:
   - **`CLA-U4`** -- no retired string survives into rendered founder-facing text: *Conversation
     history*, *Tell your Keel agent*, *Something's off*, *Ruled out*, *This isn't working*,
     *Recorded*, *Not what I meant* (`RETIRED_STRINGS` below) -- copy this policy's own history
     shows the product used to say, in the pre-round-5 surfaces this spec retires.
   - **`CLA-U5`** -- no gendered pronoun (he/him/his/she/her/hers) in an element that renders a
     participant's name (`captured_text["participant_names"]` non-empty is what makes this check
     applicable at all -- skipped, not failed, on a screen that never names a participant).
   - **`GUI-U3`** -- every waiting state names what is waited for: the wait box/typing indicator's
     own captured text (`captured_text["waiting_text"]`) must be sentence-shaped (>= 3 words), not
     a bare spinner with no words at all. Skipped when this visit never rendered a waiting state.

   Category weights are unchanged in *value* (FIDELITY 0.4/GUIDANCE 0.25/ORIENTATION 0.2/CLARITY
   0.15) -- "renormalised" here means what a category's own score is now a mean *over*: FIDELITY
   over four hops instead of eight, GUIDANCE/ORIENTATION over UI-only checks instead of UI-plus-
   wire ones. The four weights still sum to 1.0 and nothing here changes `score_categories`'s math
   (`harness/scoring.py`), only which checks feed it.
"""

from __future__ import annotations

import re
from typing import Any

POLICY_VERSION = 6

CATEGORY_WEIGHTS: dict[str, float] = {
    "FIDELITY": 0.4,
    "GUIDANCE": 0.25,
    "ORIENTATION": 0.2,
    "CLARITY": 0.15,
}

DEFAULT_WEIGHT = 1
# Policy v6 (module docstring, judgement call 9): the weight-2 rule for verbatim participant
# speech moves to where that speech is actually captured now that there is no wire client to
# capture an `interpret_context` hop from -- the participant's own typed answer, read back on
# the founder's own People page.
FID_ANSWER_PARTICIPANT_PAGE_WEIGHT = 2

COMPLETION_GATE_SCORE = 2.0

# The non-FID checks this policy defines: id -> {attribute, weight}. FID-* checks are generated
# per fact x hop from the scenario's fact registry (harness/rubric.py), always attribute
# "FIDELITY", weighted by `fid_weight` below.
CHECKS: dict[str, dict[str, Any]] = {
    "ORI-U1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-U2": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-P1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "GUI-U1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "GUI-P1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "CLA-U1": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "CLA-U2": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    # Policy v3: verdictLabel/needLabel, read off a ui_visit's own captured `state` snapshot.
    "CLA-U3": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    # Policy v4 (module docstring, judgement call 6): the arrival read's own greeting, the locked
    # People section's own why, and the pointer-to-agent sentence's own missing door.
    "CLA-AR1": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "ORI-U3": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "GUI-U2": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    # Policy v6 (module docstring, judgement call 9): no retired string, no gendered pronoun for
    # a participant, every waiting state names what is waited for.
    "CLA-U4": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "CLA-U5": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "GUI-U3": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
}

# Policy v4: a raw project id (UUID) has no business appearing in a founder-facing arrival
# greeting -- CLA-AR1's "id-free" half. Distinct from CLARITY_TOKENS (enum vocabulary): a UUID is
# never a fixed token this policy could enumerate.
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")

# Every hop id this policy knows how to score (data-model.md's Fact registry), pruned to the four
# a screen or the participant survey can actually carry (policy v6, judgement call 9) -- the wire-
# only hops (`agent_echo`, `interpret_context`, `recorded`, `roles_context`, `chat_turns`) are
# retired with the agent-protocol harness.
HOP_IDS = ["stage_screen", "invite_screen", "participant_page", "brief"]

# hop ids reached via a ui_visit interaction's captured_text vs. a participant_visit's -- lets
# harness/rubric.py know which interactions are even candidates for a given hop.
# `participant_page` is reachable from either: the participant's own survey render
# (`participant_visit`), or the founder's later read-back of it verbatim (a `ui_visit` on the
# People page's "See <name>'s answers" popup, spec 005 US2 step 6's P9) -- both are legitimate
# places an answer's fidelity can be judged, and a scenario may capture either or both.
HOP_INTERACTION_TYPES: dict[str, tuple[str, ...]] = {
    "stage_screen": ("ui_visit",),
    "invite_screen": ("ui_visit",),
    "brief": ("ui_visit",),
    "participant_page": ("participant_visit", "ui_visit"),
}

# Waivers (design §5): (fact kind, hop id) -> {reason, reference}. A waived hop counts as pass,
# flagged, provided the hop's interaction actually exists (waivers excuse summarizing, not total
# absence -- see harness/rubric.py).
WAIVERS: dict[tuple[str, str], dict[str, str]] = {
    ("assumption", "brief"): {
        "id": "brief-findings-summarize",
        "reason": "Brief.findings is a founder-authored summary sentence (with respondent counts), "
                  "not a verbatim repeat of the assumption statement -- known, accepted contract gap.",
        "reference": "keel-cloud canon/api-design.md §6a",
    },
}


def fid_weight(fact_kind: str, hop: str) -> int:
    if fact_kind == "answer" and hop == "participant_page":
        return FID_ANSWER_PARTICIPANT_PAGE_WEIGHT
    return DEFAULT_WEIGHT


def waiver_for(fact_kind: str, hop: str) -> dict[str, str] | None:
    return WAIVERS.get((fact_kind, hop))


# ---------------------------------------------------------------------------------- normalization

_QUOTE_MAP = str.maketrans({
    "“": '"', "”": '"', "‘": "'", "’": "'", "`": "'",
})
_TRAILING_PUNCT_RE = re.compile(r"[.,!?;:]+$")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize(text: str | None) -> str:
    """casefold, collapse whitespace, unify quotes/apostrophes, strip trailing punctuation
    (contract's Normalization section) -- applied to both a fact's declared text and the hop
    blob it's checked against, so `"Payroll…"` matches `'payroll...'` and matching stays
    verbatim-by-default rather than fuzzy.
    """
    if not text:
        return ""
    t = text.translate(_QUOTE_MAP).casefold()
    t = _WHITESPACE_RE.sub(" ", t).strip()
    t = _TRAILING_PUNCT_RE.sub("", t).strip()
    return t


def fact_reaches_hop(fact_text: str, hop_blob: str) -> bool:
    """Verbatim-by-default matching: does the normalized fact text appear, intact, inside the
    normalized hop blob? Substring rather than equality because a hop blob is a whole screen's
    (or context payload's) text, not just the one fact.
    """
    needle = normalize(fact_text)
    if not needle:
        return False
    return needle in normalize(hop_blob)


# -------------------------------------------------------------------------------------- clarity

WORKFLOW_STATES = {"OPEN", "READY_TO_BUILD", "PIVOTED", "STOPPED"}
VERDICTS = {"UNTESTED", "SUPPORTED", "CONTRADICTED", "MIXED"}
NEEDS = {"REVIEW", "INVITE", "ANSWERS", "EVIDENCE", "REFRAME"}
RISKS = {"LOAD_BEARING", "SUPPORTING"}
HANDLE_NAMES = {"opportunity", "assumptions", "contradictions", "roles", "response",
                "link_questions", "brief_inputs", "awaiting"}
ACTION_NAMES = {"CREATE", "FRAME", "INTRODUCE_ROLES", "INTRODUCE_ASSUMPTIONS",
                "WITHDRAW_ASSUMPTION", "INTERPRET", "PROCEED_TO_BRIEF", "PIVOT", "STOP"}
LICENSED_ACTION_NAMES = {"CREATE", "INTERPRET"}
RULE_LITERALS = {"token", "concurrency", "schema", "context", "open_web", "screen"}
# Policy v6 (module docstring, judgement call 9): the connect stack's own status vocabulary --
# the device-authorization/runtime-job states a founder-facing screen must never leak raw.
CONNECT_STATES = {"AWAITING_CONFIRMATION", "ACCEPTED", "PENDING", "RUNNING", "DONE", "EXPIRED"}

# Judgement call 5 (policy v3, live-confirmed 2026-08-30 once CLA-A2 started sweeping commit
# `display` and CLA-U1 swept the brief's own ALL-CAPS section headers): two more English-word
# collisions, the same shape as judgement call 1's StageType exemption. "roles" is FounderVoice's
# own correct copy ("Your roles are saved."), an ordinary plural noun that also happens to be a
# context-handle name. "EVIDENCE" is BriefRoute's own section heading ("What the evidence said no
# to", rendered upper-case by CSS -- `.inner_text()` returns the rendered text) colliding with the
# `Need` token of the same spelling. Sweeping either would flag the product's own correct copy,
# not a leak -- excluded for the same reason stage names are.
#
# Policy v6, the same shape again, live-confirmed on the first green S-001 run
# (`runs/20260904T020336Z-s001-smoke`, four CLA-U1 hits): the review card's own step line reads
# "STEP 2 OF 4 · THE PROBLEM · REVIEW BEFORE ANYONE IS ASKED" (`StageRoute.tsx`, rendered
# upper-case by CSS) -- "REVIEW" there is the English verb in correct founder copy, colliding with
# the `Need` token of the same spelling exactly as "EVIDENCE" does. Exempted for the same reason;
# a raw `REVIEW` leaking as a *need* token would have to arrive in mixed-case JSON to be a leak at
# all, and CLA-U2's structural sweep still catches that.
_ENGLISH_COLLISION_EXEMPTIONS = {"roles", "EVIDENCE", "REVIEW"}

# See module docstring, judgement call 1: StageType names are excluded on purpose.
CLARITY_TOKENS: set[str] = (
    WORKFLOW_STATES | VERDICTS | NEEDS | RISKS | HANDLE_NAMES
    | (ACTION_NAMES - LICENSED_ACTION_NAMES) | RULE_LITERALS | CONNECT_STATES
) - _ENGLISH_COLLISION_EXEMPTIONS

# Policy v6, CLA-U4: strings the pre-round-5 surfaces this spec retires used to show a founder --
# a literal survival of any of these into rendered text means a retired screen variant leaked
# back in, not a new coincidence (none of the seven collides with ordinary English the way
# judgement call 1/5's exemptions did, so no exemption list is needed here).
RETIRED_STRINGS = {
    "Conversation history", "Tell your Keel agent", "Something's off", "Ruled out",
    "This isn't working", "Recorded", "Not what I meant",
}

# Policy v6, CLA-U5: a participant is never known to be one gender or another -- these six read
# straight off the check's own name ("no gendered pronoun"), not a closed linguistic catalogue.
GENDERED_PRONOUNS = {"he", "him", "his", "she", "her", "hers"}
_WORD_RE = re.compile(r"[A-Za-z']+")

_URL_RE = re.compile(r"\S+://\S+")
_CAMEL_CASE_RE = re.compile(r"\b[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*\b")
_JSON_PUNCT_RE = re.compile(r'[{}\[\]]|"\s*:\s*"?|\'\s*:\s*\'?')


def _strip_urls(text: str) -> str:
    """CLARITY exempts URL path segments (design §3/spec edge cases) -- strip whole URL tokens
    (scheme://...) before sweeping, so a captured page URL or invite link doesn't trip the enum
    or field-name sweep on its path segments.
    """
    return _URL_RE.sub(" ", text)


def enum_violations(text: str | None) -> list[str]:
    """Raw enum tokens found verbatim (case-sensitive, whole-word) in `text`, minus the URL
    exemption and the two licensed action names (already excluded from CLARITY_TOKENS)."""
    if not text:
        return []
    scanned = _strip_urls(text)
    return sorted({token for token in CLARITY_TOKENS if re.search(rf"\b{re.escape(token)}\b", scanned)})


def structural_violations(text: str | None) -> list[str]:
    """JSON punctuation and camelCase field names found in `text` (CLA-U2 / half of CLA-A1)."""
    if not text:
        return []
    scanned = _strip_urls(text)
    found = {m.group(0) for m in _CAMEL_CASE_RE.finditer(scanned)}
    found |= {m.group(0) for m in _JSON_PUNCT_RE.finditer(scanned) if m.group(0).strip()}
    return sorted(found)


def clarity_violations(text: str | None) -> list[str]:
    """Combined sweep (CLA-A1's "free of raw enums ... and field names")."""
    return sorted(set(enum_violations(text)) | set(structural_violations(text)))


def retired_string_violations(text: str | None) -> list[str]:
    """CLA-U4 (policy v6): any of `RETIRED_STRINGS` found verbatim (case-sensitive substring --
    these are whole phrases, not single tokens, so the whole-word regex `enum_violations` uses
    would be the wrong tool)."""
    if not text:
        return []
    scanned = _strip_urls(text)
    return sorted({phrase for phrase in RETIRED_STRINGS if phrase in scanned})


def gendered_pronoun_violations(text: str | None) -> list[str]:
    """CLA-U5 (policy v6): any of `GENDERED_PRONOUNS` found as a whole word, case-insensitive."""
    if not text:
        return []
    words = {w.lower() for w in _WORD_RE.findall(text)}
    return sorted(words & GENDERED_PRONOUNS)
