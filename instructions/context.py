"""The `context` object a screen would have been given (spec 009 FR-005, data-model.md §3).

Every key `context-keys.json` names for the screen, **in that order**, `null` where the corpus has
no value. Order is load-bearing: `ScreenContextBuilder` returns a `LinkedHashMap` "so the AI reads
the rendered object in exactly the order this class writes it", and a harness that assembled the
same keys in a different order would be measuring a different prompt. Nothing here decides which
keys exist -- keel-cloud's exporter does, and an unknown key is filled with `None` rather than
dropped, so a screen that gains one is visible in the prompt instead of silently absent.
"""

from __future__ import annotations

# data-model.md note 2: the corpus writes the tap the way a person reads it; the wire wants the
# enum name. One table, here, because it is the only place the two vocabularies meet.
TAP_ENUM = {
    "hasn't happened": "HASNT_HAPPENED",
    "hasnt happened": "HASNT_HAPPENED",
    "it hasn't happened": "HASNT_HAPPENED",
    "can't recall": "CANT_RECALL",
    "cant recall": "CANT_RECALL",
    "rather not say": "RATHER_NOT_SAY",
}

_STATEMENT_KEYS = {
    "problem_statement": "PROBLEM",
    "solution_statement": "SOLUTION",
    "commercial_statement": "COMMERCIAL",
}

# research.md R5a: a corpus entry lists its roles flat and records no creating stage, so which
# stage introduced which role is read off the `askedOf` edge -- the only evidence in the file.
_EARLIER_STAGES = {"PROBLEM": (), "SOLUTION": ("PROBLEM",), "COMMERCIAL": ("PROBLEM", "SOLUTION")}


def tap_enum(tap):
    """The enum name for a corpus tap, or `None` for no tap. An unknown tap is passed through
    upper-cased rather than dropped, so a corpus that grew a tap shows up in the prompt as itself
    instead of disappearing."""
    if tap is None:
        return None
    key = str(tap).strip().lower()
    return TAP_ENUM.get(key, key.upper().replace(" ", "_").replace("'", ""))


def roles_for(entry, stage: str) -> list:
    """`existing_roles` for a stage: the roles the earlier stages' beliefs are asked of (R5a).

    `[]` for PROBLEM -- production's own state, since the problem screen is where roles are first
    invented. The set supplied is recorded on the case, because a duplicate-heavy extras list is
    more often this reading being wrong than the instruction being wrong.
    """
    wanted, seen = [], set()
    for earlier in _EARLIER_STAGES.get(stage, ()):
        for belief in entry.beliefs_for(earlier):
            if belief.asked_of and belief.asked_of not in seen:
                seen.add(belief.asked_of)
                wanted.append(belief.asked_of)
    entries = []
    for role_id in wanted:
        role = entry.role(role_id) or {}
        item = {
            "id": role_id,
            "label": role.get("label", role_id),
            "roleType": role.get("roleType"),
            "about": role.get("about", ""),
        }
        if role.get("market"):
            item["market"] = role["market"]
        entries.append(item)
    return entries


def anchors_for(entry, person) -> list:
    """`anchors[]` for the reading screen: one entry per anchor this person wrote text under.

    **A blank anchor is not offered at all**, exactly as `ScreenContextBuilder.anchorsWritten`
    skips it -- so a blank never reaches the model, never appears in `answered`, and can never be
    in any denominator.
    """
    anchors = []
    for anchor_id, answer in person.written():
        golden_anchor = entry.anchor(anchor_id) or {}
        anchors.append({
            # stage travels beside anchor_id, first (measured-beliefs decision 18, DRIFT #37):
            # `ScreenContextBuilder.anchorsWritten` writes it because a link can carry occasions
            # from more than one approved stage and every stage's own questionnaire numbers its
            # first occasion A1 -- the pair, not the bare id, is what tells two occasions apart.
            "stage": golden_anchor.get("stage"),
            "anchor_id": anchor_id,
            "prompt": golden_anchor.get("prompt"),
            "text": answer.get("text"),
            "tap": tap_enum(answer.get("tap")),
        })
    return anchors


def _statement(entry, stage: str):
    """The corpus writes `statements: {problem: ..., solution: ...}` in lower case; the aggregate's
    own `StageType` is upper. Read either, so a stage's statement can never silently be `null` --
    which is the one value that would make an assumption screen legitimately ask (decision 14) and
    turn every case in the run into a failure the harness caused."""
    statements = entry.statements or {}
    for key in (stage, stage.lower(), stage.title()):
        if statements.get(key):
            return statements[key]
    return None


def build_assumptions(entry, stage: str, keys: list) -> dict:
    """One assumption screen's context, filled key by key in the exporter's own order."""
    context = {}
    for key in keys:
        if key in _STATEMENT_KEYS:
            context[key] = _statement(entry, _STATEMENT_KEYS[key])
        elif key == "market":
            context[key] = entry.market or None
        elif key == "existing_roles":
            context[key] = roles_for(entry, stage)
        elif key == "project_name":
            context[key] = entry.title
        else:
            # A key keel-cloud added that this harness has no value for. `None` rather than an
            # omission: the builder always writes every key for its screen, absent value and all.
            context[key] = None
    return context


# ------------------------------------------------------------------------------- the BRIEF screen

# `ScreenContextBuilder.claimsWithStandings` iterates `StageType.values()`, so the three claims
# arrive in the founder's own order and all three are always present.
_BRIEF_STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")


def build_brief(entry, keys: list) -> dict:
    """The `BRIEF` screen's context: what the founder called it, where they sell, and the three
    claims with every line's standing under them (keel-cloud spec 030 FR-009).

    `ScreenContextBuilder`'s BRIEF case writes exactly three keys --

        context.put("project_name", project.name().orElse(null));
        context.put("market", market(project.market().orElse(null)));
        context.put("claims", claimsWithStandings(project));

    -- and this fills them from the entry's own `expected.standings` and nothing else, in the
    exporter's own key order like every other screen here.
    """
    context = {}
    for key in keys:
        if key == "project_name":
            context[key] = entry.title
        elif key == "market":
            context[key] = market_of(entry)
        elif key == "claims":
            context[key] = claims_for(entry)
        else:
            context[key] = None
    return context


def market_of(entry) -> dict | None:
    """`ScreenContextBuilder.market`'s own three keys, in its own order."""
    market = entry.market or {}
    if not market:
        return None
    return {"country": market.get("country"), "region": market.get("region"),
            "language": market.get("language")}


def claims_for(entry) -> list:
    """`claimsWithStandings`: `{stage, statement, approved, verdict, drift, beliefs}` x 3.

    A stage the entry judges is `approved` -- the corpus's `expected.stages` is the aggregate's
    verdict *after* approval and reading, and there is no unapproved stage in this frozen set. One
    that carries no verdict is unapproved, and then carries no beliefs and a `null` verdict and
    drift, exactly as the builder writes it (product-constitution §5.1: there is no status at all
    before approval, and the paragraph must not invent one).
    """
    stages = (entry.expected or {}).get("stages") or {}
    claims = []
    for stage in _BRIEF_STAGES:
        verdict = stages.get(stage)
        approved = verdict is not None
        claims.append({
            "stage": stage,
            "statement": _statement(entry, stage),
            "approved": approved,
            "verdict": str(verdict).upper() if approved else None,
            # `Project.driftOfStage` is keel-cloud's, and this repo does not own it (see the
            # module docstring's own rule and `runs/DRIFT.md` #45's lesson) -- the corpus carries
            # no stage drift, so the key is written and left `null` rather than derived here.
            "drift": None,
            "beliefs": belief_standings(entry, stage) if approved else [],
        })
    return claims


def belief_standings(entry, stage: str) -> list:
    """`beliefStandings`: fourteen fields a line, in the builder's own order.

    Three of them the corpus does not evidence, and each is written and left `null` rather than
    computed here (`build_assumptions`'s own rule, one layer down):

    - `below` / `above` -- `expected.standings` records which side a line drifted to and not how
      many people were on it.
    - `median_reads` -- keel-cloud renders this with `Measure.say`, which rounds and re-units
      ("45 minutes", "£7.50"); see `median_reads()` for what is handed over instead and why.
    """
    standings = (entry.expected or {}).get("standings") or {}
    out = []
    for belief in entry.beliefs_for(stage):
        standing = standings.get(belief.id) or {}
        out.append({
            "heading": belief.heading or None,
            "statement": belief.statement,
            "risk": belief.risk,
            "mark": belief.mark,
            "founder_phrase": belief.founder_phrase,
            "verdict": str(standing.get("verdict") or "").upper() or None,
            "drift": str(standing.get("drift") or "").upper() or None,
            "median_reads": median_reads(belief, standing),
            "inside": standing.get("inside"),
            "outside": standing.get("outside"),
            "below": None,
            "above": None,
            "guessed": standing.get("guessed"),
            "escaped": standing.get("escaped", 0),
        })
    return out


def median_reads(belief, standing: dict) -> str | None:
    """The middle answer, **in the measure's own spoken unit and not keel-cloud's phrase**.

    `ScreenContextBuilder` writes `band.measure().say(standing.median())`, and `Measure.say` is a
    piece of keel-cloud the referee does not own: it rounds minutes to the nearest five above ten,
    climbs to the largest unit a person would use, and puts the market's currency symbol on money.
    Copying it here would be `runs/DRIFT.md` #33/#36/#41/#44/#45 for the sixth time -- the referee
    holding its own copy of something it does not own -- and a paragraph would then be scored
    against this repo's arithmetic rather than the product's.

    So the number is handed over as the corpus writes it, in the unit the corpus writes it in:
    `0.75 hours`, not `45 minutes`. **That is a deviation from the context production builds, and
    it is named in the report rather than hidden.** It also sharpens the one rule this subject can
    check hardest: brief.md says *you quote it exactly -- not forty-five minutes, not 0.75 hours,
    not about three quarters of an hour*, and a model handed `0.75 hours` that writes `45 minutes`
    has converted a number it was told never to convert.

    `None` for a `CHOICE`, which has no band and so no middle to have -- exactly as keel-cloud
    writes `null` for anything that is not an `Interval`.
    """
    if belief.type != "INTERVAL":
        return None
    median = standing.get("median")
    if median is None:
        return None
    unit = (belief.measure or {}).get("unit")
    if isinstance(median, float) and median.is_integer():
        median = int(median)
    return f"{median} {unit}" if unit else str(median)


def build_reading(entry, person, keys: list) -> dict:
    """The reading screen's whole world: an invitation id and the occasions written under."""
    context = {}
    for key in keys:
        if key == "invitation_id":
            context[key] = invitation_id(entry, person)
        elif key == "anchors":
            context[key] = anchors_for(entry, person)
        else:
            context[key] = None
    return context


def invitation_id(entry, person) -> str:
    """A stable synthetic id -- no invitation exists, and the reading result must echo this back."""
    return f"{entry.id}/{person.person}"
