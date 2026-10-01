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

#: The founder's own order, which is `StageType.values()`'s. Every walk that numbers something
#: project-wide -- `earlier_lines`, `measurements`, `claims` -- walks it in this order and no other,
#: because an ordinal that meant one belief here and another in the aligner is the one failure a
#: reference by ordinal has to make impossible.
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")


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
            # **No `stage`** (`MARKS_VERSION` 8, judgement call 24; keel-cloud spec 049).
            # `anchorsWritten` used to write one because every stage's own questionnaire numbered
            # its first occasion `A1` and the pair was what told two occasions apart. There is one
            # questionnaire a project now, `Q7` is project-wide, and a merged occasion serves more
            # than one stage's beliefs -- so a `stage` here would name nothing. `interpret.md` has
            # described its context as `{anchor_id, prompt, text, tap}` all along (design §5.2).
            "anchor_id": anchor_id,
            "prompt": golden_anchor.get("prompt"),
            "text": answer.get("text"),
            "tap": tap_enum(answer.get("tap")),
        })
    return anchors


# --------------------------------------------------------------- the earlier stages' lines (049)

def measure_of(belief) -> dict | None:
    """`{kind, unit, per}` for an `INTERVAL`; **present and `None`** for a Choice, which has none.

    `ScreenContextBuilder.measureOf`'s own shape and its own three keys, in its own order.
    """
    if belief.type != "INTERVAL":
        return None
    measure = belief.measure or {}
    return {"kind": measure.get("kind"), "unit": measure.get("unit"), "per": measure.get("per")}


def band_of(belief) -> dict:
    """`{lower, upper}` with their `inclusive`/`exact` flags for an `INTERVAL`,
    `{options, expected}` for a `CHOICE` (design §6A.4, `ScreenContextBuilder.bandOf`).

    **The flags are carried, not dropped.** A reference copies the band and not only the measure,
    and `BucketBuilder` builds a different scale for an exclusive bound than for an inclusive one.
    """
    expectation = belief.expectation or {}
    if belief.type == "INTERVAL":
        return {"lower": _bound(expectation.get("lower")),
                "upper": _bound(expectation.get("upper"))}
    return {"options": list(expectation.get("options") or []),
            "expected": expectation.get("expected")}


def _bound(raw):
    if not isinstance(raw, dict):
        return None
    return {"value": raw.get("value"), "inclusive": bool(raw.get("inclusive", True)),
            "exact": bool(raw.get("exact", False))}


def _role_label(entry, role_id: str):
    return (entry.role(role_id) or {}).get("label", role_id) if role_id else None


def earlier_lines(entry, stage: str) -> list:
    """`earlier_lines` for an assumptions screen: the approved earlier stages' lines (design §6A.4).

    **Exactly eight keys -- seven things, since `stage` and `line` are one handle**: `stage`,
    `line` (**1-based within its own stage**), `heading`, `statement`, `measure`, `band`, `role`
    (the role's *label*) and `risk`. And deliberately not `mark`, not `founderPhrase`, not
    `selection` and no id at all -- the whole point of `{stage, line}` is that it is an ordinal into
    a list this side numbered, never a UUID a model has to copy back.

    `[]` for `PROBLEM`, which has no earlier stage -- and the key is then simply not sent, exactly
    as `putEarlierLines` returns without writing it.

    **This is the list `align.resolve_reads` resolves a `reads` against**, because it is the list
    this eval numbered and sent. Same walk, same order, one place -- an ordinal that meant one
    belief in the context and another in the aligner is the failure the reference design exists to
    make impossible.
    """
    lines = []
    for earlier in _EARLIER_STAGES.get(stage, ()):
        for number, belief in enumerate(entry.beliefs_for(earlier), start=1):
            lines.append({
                "stage": earlier,
                "line": number,
                "heading": belief.heading or None,
                "statement": belief.statement,
                "measure": measure_of(belief),
                "band": band_of(belief),
                "role": _role_label(entry, belief.asked_of),
                "risk": belief.risk,
            })
    return lines


# --------------------------------------------------------------------- the QUESTIONS screen (048)

def measurements_for(entry) -> list:
    """`measurements[]`: every settled belief on the project, **indexed 0-based project-wide**.

    `ScreenContextBuilder.measurements`' own eight keys in its own order -- `index`, `stage`,
    `heading`, `statement`, `risk`, `mark`, `role`, `expectation`. `stage` is a label here and the
    index is the key, which is the same move `earlier_lines` makes one screen earlier.

    Every corpus belief owns its own measurement (the frozen set was authored by hand against one
    questionnaire and restates nothing), so nothing is filtered out here the way
    `measurementsOf`'s `ownsItsMeasurement()` filters a referencing belief out in production.
    """
    out = []
    for stage in STAGES:
        for belief in entry.beliefs_for(stage):
            out.append({
                "index": len(out),
                "stage": stage,
                "heading": belief.heading or None,
                "statement": belief.statement,
                "risk": belief.risk,
                "mark": belief.mark,
                "role": _role_label(entry, belief.asked_of),
                "expectation": belief.expectation or {},
            })
    return out


def stage_statements(entry) -> dict:
    """`stage_statements`: each stage's own statement, keyed by stage, `None` where none is framed.

    All three keys always, the way `market` is always written: a key that appears and disappears is
    a key the instruction has to write two paragraphs about.
    """
    return {stage: _statement(entry, stage) for stage in STAGES}


def build_questions(entry, keys: list) -> dict:
    """The one `QUESTIONS` screen's context (keel-cloud 048 FR-011), and no more.

    `{project_name, market, founder_name, stage_statements, measurements[]}`, filled key by key in
    the exporter's own order like every other screen here.

    **`founder_name` is `None`, and that is the corpus and not a gap.** A corpus entry records a
    project, its market, its roles and its people; it records nobody's name for the founder, so the
    key is written and left `null` rather than invented -- `build_brief`'s own rule for `drift` and
    `below`/`above`, one screen along. The instruction uses it to address the participant, which no
    mark reads.
    """
    context = {}
    for key in keys:
        if key == "project_name":
            context[key] = entry.title
        elif key == "market":
            context[key] = market_of(entry)
        elif key == "stage_statements":
            context[key] = stage_statements(entry)
        elif key == "measurements":
            context[key] = measurements_for(entry)
        else:
            context[key] = None
    return context


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
# arrive in the founder's own order and all three are always present -- `STAGES` above, under the
# name this screen has called it since spec 009.
_BRIEF_STAGES = STAGES


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
