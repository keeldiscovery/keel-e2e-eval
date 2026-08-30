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
"""

from __future__ import annotations

import re
from typing import Any

POLICY_VERSION = 3

CATEGORY_WEIGHTS: dict[str, float] = {
    "FIDELITY": 0.4,
    "GUIDANCE": 0.25,
    "ORIENTATION": 0.2,
    "CLARITY": 0.15,
}

DEFAULT_WEIGHT = 1
# "FID checks on `answer` facts at `interpret_context` (weight 2 -- verbatim participant speech
# is the product's evidence spine)."
FID_ANSWER_INTERPRET_WEIGHT = 2

COMPLETION_GATE_SCORE = 2.0

# The non-FID checks this policy defines: id -> {attribute, weight}. FID-* checks are generated
# per fact x hop from the scenario's fact registry (harness/rubric.py), always attribute
# "FIDELITY", weighted by `fid_weight` below.
CHECKS: dict[str, dict[str, Any]] = {
    "ORI-A1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-A2": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-H1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-U1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-U2": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "ORI-P1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "GUI-A1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "GUI-A2": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "GUI-H1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "GUI-U1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "GUI-P1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "CLA-U1": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "CLA-U2": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    "CLA-A1": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    # 003-eval-set (S-007, design §3/§6.1): a wire refusal's {rule, problem, remedy} is agent-
    # facing text (the same status as instruction/requirements under policy v2, evals/policy.py's
    # judgement call 3) -- checked for presence/actionability (GUIDANCE, ORIENTATION), never
    # vocabulary-swept (no CLA-R* check exists, deliberately, matching v2's recalibration).
    "ORI-R1": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "GUI-R1": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    # Policy v3 (module docstring, judgement call 4): the commit `display` every agent-cycle now
    # carries, checked exactly like a handoff's own display always was.
    "ORI-A3": {"attribute": "ORIENTATION", "weight": DEFAULT_WEIGHT},
    "GUI-A3": {"attribute": "GUIDANCE", "weight": DEFAULT_WEIGHT},
    "CLA-A2": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
    # Policy v3: verdictLabel/needLabel, read off a ui-visit's own captured `state` snapshot.
    "CLA-U3": {"attribute": "CLARITY", "weight": DEFAULT_WEIGHT},
}

# Every hop id this policy knows how to score (data-model.md's Fact registry). "recorded" is
# policy v3's addition (module docstring, judgement call 4): an agent-cycle's own played-back
# commit, alongside the six the contract originally named.
HOP_IDS = ["agent_echo", "stage_screen", "invite_screen", "participant_page", "interpret_context",
           "brief", "recorded"]

# hop ids reached via an agent-cycle interaction's captured_text vs. a screen visit's -- lets
# harness/rubric.py know which interactions are even candidates for a given hop.
HOP_INTERACTION_TYPES: dict[str, tuple[str, ...]] = {
    "agent_echo": ("agent-cycle",),
    "interpret_context": ("agent-cycle",),
    "recorded": ("agent-cycle",),
    "stage_screen": ("ui-visit",),
    "invite_screen": ("ui-visit",),
    "brief": ("ui-visit",),
    "participant_page": ("participant-page",),
}

# Waivers (design §5): (fact kind, hop id) -> {reason, reference}. A waived hop counts as pass,
# flagged, provided the hop's interaction actually exists (waivers excuse summarizing, not total
# absence -- see harness/rubric.py).
WAIVERS: dict[tuple[str, str], dict[str, str]] = {
    ("assumption", "brief"): {
        "id": "brief-findings-summarize",
        "reason": "Brief.findings is a founder-authored summary sentence (with respondent counts), "
                  "not a verbatim repeat of the assumption statement -- known, accepted contract gap.",
        "reference": "keel-cloud specs/projectv2/api-design.md §6a",
    },
}


def fid_weight(fact_kind: str, hop: str) -> int:
    if fact_kind == "answer" and hop == "interpret_context":
        return FID_ANSWER_INTERPRET_WEIGHT
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

# Judgement call 5 (policy v3, live-confirmed 2026-08-30 once CLA-A2 started sweeping commit
# `display` and CLA-U1 swept the brief's own ALL-CAPS section headers): two more English-word
# collisions, the same shape as judgement call 1's StageType exemption. "roles" is FounderVoice's
# own correct copy ("Your roles are saved."), an ordinary plural noun that also happens to be a
# context-handle name. "EVIDENCE" is BriefRoute's own section heading ("What the evidence said no
# to", rendered upper-case by CSS -- `.inner_text()` returns the rendered text) colliding with the
# `Need` token of the same spelling. Sweeping either would flag the product's own correct copy,
# not a leak -- excluded for the same reason stage names are.
_ENGLISH_COLLISION_EXEMPTIONS = {"roles", "EVIDENCE"}

# See module docstring, judgement call 1: StageType names are excluded on purpose.
CLARITY_TOKENS: set[str] = (
    WORKFLOW_STATES | VERDICTS | NEEDS | RISKS | HANDLE_NAMES
    | (ACTION_NAMES - LICENSED_ACTION_NAMES) | RULE_LITERALS
) - _ENGLISH_COLLISION_EXEMPTIONS

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
