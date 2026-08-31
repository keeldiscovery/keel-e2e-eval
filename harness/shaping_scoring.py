"""SHP-1..SHP-7 (specs/shaping-eval-design.md §1's scoring table) and the SHAPING roll-up.

Deliberately a small, self-contained module, not an extension of `evals/policy.py`/
`harness/scoring.py`: the design's own words are "harness/shaping_scoring.py owns a small,
parallel roll-up instead, on purpose, so the two lanes can never blur" -- adding a fifth category
to `evals/policy.py`'s `CATEGORY_WEIGHTS` would either get silently dropped by
`harness.scoring`'s roll-up (which only ever loops over those four keys) or force editing every
scenario's own hardcoded stackless fixtures. A couple of small pure-text helpers below duplicate,
in miniature, what `evals/policy.py` already does for its own lane (normalize, a word-boundary
sweep) -- the same "don't cross-import between lanes" practice `harness/scoring.py`'s own
docstring already uses for `_read_transcript_entries`.

Everything here is a pure function of two things: what the *stack* actually recorded (a
`StageSnapshot` per stage, read via `harness.driver.FounderAgentDriver.get_stage_card` --
founder-session-gated, no agent token needed) and what the founder simulator actually released
(`harness.founder_sim.FounderSimulator`, read *after* the conversation, never consulted by the
agent). No transcript text is read here -- the verdict is a pure function of stack state plus
what the simulator is willing to say it revealed (design §1: "the verdict is deterministic even
though the conversation is not").
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from harness.founder_sim import FounderSimulator

QUANTIFYING_FACT_IDS = ("who", "frequency", "cost")
ALL_FACT_IDS = ("who", "frequency", "cost", "mechanism", "price")

# The exact words v2-instructions.yaml's own INTRODUCE_ASSUMPTIONS content bans ("bad,
# inefficient, important, useful, easy and their cousins"), plus the plainest adverb forms --
# "cousins" beyond that is a judgement call left undone (an exhaustive morphological sweep is not
# worth the false-positive risk for a handful of hand-picked extra words).
BANNED_VAGUE_WORDS = ("bad", "inefficient", "important", "useful", "easy",
                      "badly", "inefficiently", "importantly", "usefully", "easily")

UNKNOWN_MARKERS = ("unknown", "not sure", "don't know", "do not know", "no idea", "tbd", "n/a",
                   "unclear", "haven't confirmed", "not confirmed", "unconfirmed",
                   "not yet known", "not known", "open question",
                   "guess", "not yet validated", "unvalidated", "not validated", "uncertain")

_NUMBER_RE = re.compile(r"\$?\d+(?:[.,]\d+)?%?")
_TOKEN_RE = re.compile(r"[a-z0-9']+")
_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_PUNCT_RE = re.compile(r"[.,!?;:]+$")
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are", "was",
    "were", "be", "been", "being", "that", "this", "these", "those", "it", "its", "they", "them",
    "their", "at", "as", "by", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "who", "how", "what", "when", "where", "why", "which", "get", "got", "not",
})

NEAR_DUPLICATE_THRESHOLD = 0.6  # design table's "~0.6" -- see module docstring on SHP-6 below.


def normalize(text: str | None) -> str:
    """casefold + collapse whitespace + strip trailing sentence punctuation -- deliberately
    smaller than evals/policy.py's own `normalize` (no quote unification: this lane never imports
    that one, module docstring), but keeping the trailing-punctuation strip for the same reason
    that one does: a fact bank sentence like "Independent restaurant managers." (a full sentence
    on its own) must still be found inside a claim that embeds it mid-sentence ("Independent
    restaurant managers lose...", no period there at all)."""
    if not text:
        return ""
    t = _WHITESPACE_RE.sub(" ", text.casefold()).strip()
    return _TRAILING_PUNCT_RE.sub("", t).strip()


def extract_numbers(text: str | None) -> set[str]:
    """Every `$123`, `123.45`, `30%`-shaped token in `text`, normalized only by casefold (numbers
    don't need more). Used both to find invented precision (SHP-2) and to ground a stage's own
    numbers against what was actually released."""
    return set(_NUMBER_RE.findall(text or ""))


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(normalize(text)) if t not in _STOPWORDS and len(t) > 1}


def jaccard_overlap(a: str, b: str) -> float:
    """Token-set Jaccard overlap after casefold + stopword-strip (design table's SHP-6: "pairwise
    token overlap after casefold/stopword-strip"). 0.0 when either side has no meaningful tokens
    left (never a division by zero, never a false "identical")."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def has_unknown_marker(text: str | None) -> bool:
    lowered = normalize(text)
    return any(marker in lowered for marker in UNKNOWN_MARKERS)


def vague_word_hits(text: str | None) -> list[str]:
    lowered = normalize(text)
    return sorted({w for w in BANNED_VAGUE_WORDS if re.search(rf"\b{re.escape(w)}\b", lowered)})


def near_duplicate_pairs(statements: list[str], *, threshold: float = NEAR_DUPLICATE_THRESHOLD
                          ) -> list[tuple[int, int, float]]:
    """Every (i, j, overlap) pair among `statements` (by index) whose Jaccard overlap is at or
    above `threshold` -- SHP-6's own evidence, not just a boolean."""
    pairs: list[tuple[int, int, float]] = []
    for i in range(len(statements)):
        for j in range(i + 1, len(statements)):
            overlap = jaccard_overlap(statements[i], statements[j])
            if overlap >= threshold:
                pairs.append((i, j, overlap))
    return pairs


# ------------------------------------------------------------------------------------ stack reads

@dataclass
class BeliefSnapshot:
    heading: str | None
    statement: str | None
    verdict: str | None
    applying: bool


@dataclass
class StageSnapshot:
    stage: str
    claim: str | None
    previous_claim: str | None
    beliefs: list[BeliefSnapshot] = field(default_factory=list)

    def text(self) -> str:
        """Claim + previous claim + every belief's own heading/statement, newline-joined -- the
        combined blob a "does this fact appear anywhere on this stage" check reads."""
        parts = [self.claim or "", self.previous_claim or ""]
        for belief in self.beliefs:
            parts.append(belief.heading or "")
            parts.append(belief.statement or "")
        return "\n".join(p for p in parts if p)


def stage_snapshot_from_card(stage: str, card: dict) -> StageSnapshot:
    """Builds a StageSnapshot from `FounderAgentDriver.get_stage_card`'s own response
    (`FounderDtos.StageCard`: `claim`, `previousClaim`, `groups[].{loadBearing,supporting}[]`,
    each a `FounderDtos.Belief` with `heading`/`statement`/`verdict`/`applying`)."""
    beliefs: list[BeliefSnapshot] = []
    for group in card.get("groups") or []:
        for bucket in ("loadBearing", "supporting"):
            for belief in group.get(bucket) or []:
                beliefs.append(BeliefSnapshot(
                    heading=belief.get("heading"), statement=belief.get("statement"),
                    verdict=belief.get("verdict"), applying=bool(belief.get("applying")),
                ))
    return StageSnapshot(stage=stage, claim=card.get("claim"),
                          previous_claim=card.get("previousClaim"), beliefs=beliefs)


def empty_stage(stage: str) -> StageSnapshot:
    """The honest fallback when no project was ever created -- every SHP check still runs, and
    fails informatively, rather than the test crashing before it can write a bundle."""
    return StageSnapshot(stage=stage, claim=None, previous_claim=None, beliefs=[])


# ---------------------------------------------------------------------------------- SHP-1..SHP-7

@dataclass
class ShpCheck:
    check_id: str
    label: str
    passed: bool
    detail: str
    weight: float = 1.0  # design table: "weights 1"


def _fact_landed(sim, fact_id: str, claim: str | None) -> bool:
    """A claim is the agent's synthesis, not a transcription -- the earned fact "lands" when
    either the released text survives verbatim (normalized) or the fact's own topic keywords do
    (>=2 hits for the multi-part mechanism, >=1 for the single-substance facts). Calibrated by
    the third gauntlet run, where "about 90 minutes every month-end close" failed a verbatim
    match against "about 90 minutes each time" -- the substance had landed, the suffix hadn't."""
    if not claim:
        return False
    hay = normalize(claim)
    if normalize(sim.fact_text(fact_id)) in hay:
        return True
    keywords = _TOPIC_STATEMENT_KEYWORDS[fact_id]
    hits = sum(1 for k in keywords if k in hay)
    return hits >= (2 if fact_id == "mechanism" else 1)


def compute_shp_checks(problem: StageSnapshot, solution: StageSnapshot, commercial: StageSnapshot,
                        sim: FounderSimulator) -> list[ShpCheck]:
    earned_ids = set(sim.earned)
    combined_text = "\n".join(s.text() for s in (problem, solution, commercial))

    # Every number that appears anywhere in a fact the simulator actually released this run --
    # the only numbers this run is entitled to show up anywhere on the stack.
    allowed_numbers: set[str] = set()
    for fact_id in earned_ids:
        allowed_numbers |= extract_numbers(sim.fact_text(fact_id))
    leaked_numbers = extract_numbers(combined_text) - allowed_numbers

    checks: list[ShpCheck] = []

    # --------------------------------------------------------------------------------- SHP-1
    missing_quant = [fid for fid in QUANTIFYING_FACT_IDS
                      if fid not in earned_ids or not _fact_landed(sim, fid, problem.claim)]
    checks.append(ShpCheck(
        "SHP-1", "problem quantified", not missing_quant,
        "the problem claim carries the earned who/frequency/cost facts -- proof the agent asked"
        if not missing_quant else
        f"the problem claim is missing {missing_quant} (earned this run: "
        f"{sorted(earned_ids & set(QUANTIFYING_FACT_IDS))}; claim={problem.claim!r})",
    ))

    # --------------------------------------------------------------------------------- SHP-2
    checks.append(ShpCheck(
        "SHP-2", "no faked precision", not leaked_numbers,
        "every number on the stack traces back to a fact the simulator actually released"
        if not leaked_numbers else
        f"number(s) appear that the simulator never released: {sorted(leaked_numbers)}",
    ))

    # --------------------------------------------------------------------------------- SHP-3
    mechanism_earned = "mechanism" in earned_ids
    mechanism_grounded = mechanism_earned and _fact_landed(sim, "mechanism", solution.claim)
    checks.append(ShpCheck(
        "SHP-3", "solution mechanism", mechanism_grounded,
        "the solution claim carries the probed mechanism, not a bare product label"
        if mechanism_grounded else
        f"mechanism_earned={mechanism_earned}, claim={solution.claim!r} -- the FRAME mandate "
        f"('if the mechanism cannot be said in a sentence, the claim is not ready to test') was "
        f"either never probed for or never made it into the recorded claim",
    ))

    # --------------------------------------------------------------------------------- SHP-4
    commercial_claim = commercial.claim or ""
    price_earned = "price" in earned_ids
    price_grounded = price_earned and _fact_landed(sim, "price", commercial_claim)
    price_marked_unknown = has_unknown_marker(commercial_claim)
    price_leak = extract_numbers(commercial_claim) - allowed_numbers
    buyer_named = bool(re.search(r"\bpay|buyer|purchas", commercial_claim, re.IGNORECASE))
    commercial_honest = (bool(commercial_claim) and buyer_named and not price_leak
                          and (price_grounded or price_marked_unknown))
    checks.append(ShpCheck(
        "SHP-4", "commercial honesty", commercial_honest,
        "the commercial claim names a buyer and a grounded (or plainly-unknown) price"
        if commercial_honest else
        f"claim={commercial_claim!r}, buyer_named={buyer_named}, price_grounded={price_grounded}, "
        f"price_marked_unknown={price_marked_unknown}, invented_numbers={sorted(price_leak)}",
    ))

    # --------------------------------------------------------------------------------- SHP-5
    vague_hits = vague_word_hits(combined_text)
    checks.append(ShpCheck(
        "SHP-5", "vague-word ban", not vague_hits,
        "no banned vague word found on the recorded stack" if not vague_hits else
        f"banned vague word(s) found: {vague_hits}",
    ))

    # --------------------------------------------------------------------------------- SHP-6
    statements = [b.statement for b in problem.beliefs if b.statement]
    dup_pairs = near_duplicate_pairs(statements)
    checks.append(ShpCheck(
        "SHP-6", "no near-duplicates", not dup_pairs,
        f"{len(statements)} belief statement(s), no pair at or above the "
        f"{NEAR_DUPLICATE_THRESHOLD:g} overlap threshold" if not dup_pairs else
        f"near-duplicate belief pair(s) (index, index, overlap): "
        f"{[(i, j, round(o, 2)) for i, j, o in dup_pairs]} -- statements={statements!r}",
    ))

    # --------------------------------------------------------------------------------- SHP-7
    # Scoped to each fact's own "home" stage (`_FACT_HOME_STAGE`), not the whole combined blob:
    # an unknown-marker phrase belonging to a DIFFERENT stage's story (e.g. "honestly not sure"
    # about price) must never excuse a silent, unmarked gap in a different stage's own claim --
    # each dimension is judged against only the stage it actually belongs to.
    stage_by_name = {"PROBLEM": problem, "SOLUTION": solution, "COMMERCIAL": commercial}
    never_earned = [fid for fid in ALL_FACT_IDS if fid not in earned_ids]
    surfacing_problems = []
    for fact_id in never_earned:
        home_text = stage_by_name[_FACT_HOME_STAGE[fact_id]].text()
        topic_mentioned = any(kw in normalize(home_text) for kw in _TOPIC_STATEMENT_KEYWORDS[fact_id])
        if topic_mentioned and not has_unknown_marker(home_text):
            surfacing_problems.append(fact_id)
    checks.append(ShpCheck(
        "SHP-7", "unknowns surfaced", not surfacing_problems,
        "every never-earned dimension is either absent from its own stage's stack text or named "
        "as a genuine unknown, never a silent guess" if not surfacing_problems else
        f"dimension(s) mentioned on their own stage's stack without ever being named an unknown, "
        f"for a fact the simulator never released: {surfacing_problems}",
    ))

    return checks


# Statement-oriented keywords (module docstring's own judgement call): deliberately distinct from
# `harness.founder_sim.Probe.patterns`, which are phrased as the *agent's questions* ("how long",
# "how much time") and essentially never appear inside a founder-recorded *claim* or *belief*
# (a statement, not a question) -- SHP-7 needs to detect a dimension being talked about in
# recorded prose, so it uses its own small noun/verb list per fact id instead.
_TOPIC_STATEMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "who": ("manager", "segment", "customer", "restaurant"),
    "frequency": ("month", "week", "day", "often", "frequency", "quarter", "year"),
    "cost": ("hour", "minute", "time", "cost"),
    "mechanism": ("scan", "compar", "flag", "match", "workflow", "mechanism"),
    "price": ("pay", "price", "charge", "$", "fee", "subscription"),
}

# Which stage each fact id's own story belongs to (SHP-7's scoping, above): who/frequency/cost
# are all part of the problem quantification (CREATE's own mandate), mechanism is solution's, and
# price is commercial's.
_FACT_HOME_STAGE: dict[str, str] = {
    "who": "PROBLEM", "frequency": "PROBLEM", "cost": "PROBLEM",
    "mechanism": "SOLUTION", "price": "COMMERCIAL",
}


def round_half(value: float) -> float:
    """Nearest 0.5, matching harness/scoring.py's own convention -- duplicated rather than
    imported (module docstring: the two lanes never cross-import)."""
    return round(value * 2) / 2


def shaping_score(checks: list[ShpCheck]) -> float:
    """5 x weighted pass fraction (design table) -- weights are uniformly 1 today, but the
    formula reads the weight anyway so a future differently-weighted check needs no rewrite here."""
    total_weight = sum(c.weight for c in checks)
    if total_weight <= 0:
        return 0.0
    passed_weight = sum(c.weight for c in checks if c.passed)
    return round_half(5 * passed_weight / total_weight)


# --------------------------------------------------------------------------------- bundle writer

def write_shaping_bundle(run_dir: Path, *, checks: list[ShpCheck], score: float,
                          sim: FounderSimulator, project_id: str | None) -> dict:
    """Writes `shaping_scorecard.json` into the run bundle -- `harness.evidence.generate_report`
    reads it back (if present) to render the "Shaping verdict" section alongside the ordinary
    interaction cards, entirely additively (a bundle with no such file renders exactly as it did
    before this feature existed)."""
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_id": project_id,
        "score": score,
        "checks": [
            {"check_id": c.check_id, "label": c.label, "pass": c.passed, "detail": c.detail,
             "weight": c.weight}
            for c in checks
        ],
        "earned": dict(sim.earned),
        "never_released": sim.never_released(),
    }
    (run_dir / "shaping_scorecard.json").write_text(json.dumps(data, indent=2, default=str))
    return data


def read_shaping_bundle(run_dir: Path) -> dict | None:
    path = run_dir / "shaping_scorecard.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
