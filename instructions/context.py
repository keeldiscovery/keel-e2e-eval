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
