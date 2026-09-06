"""Which produced belief is which golden belief (spec 009 FR-009, data-model.md §4).

**Structure first, and almost always structure only.** A belief is a stage, a type, a measure kind
and a band -- or an expected option and an option list -- and those are comparable without asking
anybody's opinion. So candidates are found by structure, pairs are scored by counting agreeing
fields, and the assignment is greedy over descending score with ties broken by golden id order, so
the same inputs always give the same alignment. Every pair this module makes is marked
`by: "structure"`; `judge.py` is the only thing that may mark one `"judge"`, and only for a genuine
tie.

**Why headings are only a tie-break.** Wording is free (design §10 step 4): a heading that reads
differently is not a wrong belief, and scoring it would make the eval grade prose. It breaks ties
between otherwise equal candidates and contributes nothing else.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# The six structural fields, plus founderPhrase -- the seven `score.py` reports separately.
FIELDS = ("type", "kind", "unit", "expected_or_band", "risk", "mark", "founder_phrase")

# data-model.md §4: two Choices are candidates when their expected options match, or their option
# sets overlap above this. Half the smaller list is the threshold -- enough that "did you recount
# or ring the supplier" and "did you recount, ring the supplier, or let it go" are one question.
OPTION_OVERLAP_THRESHOLD = 0.5


def normalise(text) -> str:
    """Case- and whitespace-normalised, for every string comparison in this module."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


@dataclass
class Pair:
    golden_id: str
    produced_index: int
    score: float
    by: str
    fields: dict


@dataclass
class Alignment:
    matched: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    extra: list = field(default_factory=list)
    ambiguous: list = field(default_factory=list)

    @property
    def judged(self) -> int:
        return sum(1 for pair in self.matched if pair.by == "judge")


# --------------------------------------------------------------------------- reading a produced belief

def produced_view(belief: dict) -> dict:
    """The fields this module compares, read out of a produced belief defensively.

    A produced belief comes from a model: any field may be missing or the wrong type, and this
    must not raise -- an unreadable belief is an unmatched one, which is a finding, not a crash.
    """
    expectation = belief.get("expectation") if isinstance(belief, dict) else None
    expectation = expectation if isinstance(expectation, dict) else {}
    measure = expectation.get("measure")
    measure = measure if isinstance(measure, dict) else {}
    options = expectation.get("options")
    return {
        "type": expectation.get("type"),
        "kind": measure.get("kind"),
        "unit": measure.get("unit"),
        "per": measure.get("per"),
        "lower": _bound(expectation.get("lower")),
        "upper": _bound(expectation.get("upper")),
        "options": [normalise(o) for o in options] if isinstance(options, list) else [],
        "expected": expectation.get("expected"),
        "risk": belief.get("risk") if isinstance(belief, dict) else None,
        "mark": belief.get("mark") if isinstance(belief, dict) else None,
        "founder_phrase": belief.get("founderPhrase") if isinstance(belief, dict) else None,
        "heading": belief.get("heading") if isinstance(belief, dict) else None,
        "statement": belief.get("statement") if isinstance(belief, dict) else None,
    }


def golden_view(belief) -> dict:
    """The same seven fields off a `corpus.GoldenBelief`, so the comparison is symmetric."""
    expectation = belief.expectation or {}
    measure = expectation.get("measure") or {}
    options = expectation.get("options")
    return {
        "type": expectation.get("type"),
        "kind": measure.get("kind"),
        "unit": measure.get("unit"),
        "per": measure.get("per"),
        "lower": _bound(expectation.get("lower")),
        "upper": _bound(expectation.get("upper")),
        "options": [normalise(o) for o in options] if isinstance(options, list) else [],
        "expected": expectation.get("expected"),
        "risk": belief.risk,
        "mark": belief.mark,
        "founder_phrase": belief.founder_phrase,
        "heading": belief.heading,
        "statement": belief.statement,
    }


def _bound(raw):
    if not isinstance(raw, dict):
        return None
    value = raw.get("value")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return {
        "value": value,
        "inclusive": bool(raw.get("inclusive", True)),
        "exact": bool(raw.get("exact", False)),
    }


# ------------------------------------------------------------------------------------- candidates

def is_candidate(golden: dict, produced: dict) -> bool:
    """data-model.md §4's candidate rule, and nothing looser."""
    if not golden.get("type") or golden.get("type") != produced.get("type"):
        return False
    if golden["type"] == "INTERVAL":
        if normalise(golden.get("kind")) != normalise(produced.get("kind")):
            return False
        return _bands_intersect(golden, produced)
    if normalise(golden.get("expected")) and \
            normalise(golden.get("expected")) == normalise(produced.get("expected")):
        return True
    return _option_overlap(golden.get("options") or [], produced.get("options") or []) \
        >= OPTION_OVERLAP_THRESHOLD


def _bands_intersect(a: dict, b: dict) -> bool:
    """An absent bound is infinite -- `at least 40` and `40 to 90` describe the same region."""
    a_lo = a["lower"]["value"] if a.get("lower") else float("-inf")
    a_hi = a["upper"]["value"] if a.get("upper") else float("inf")
    b_lo = b["lower"]["value"] if b.get("lower") else float("-inf")
    b_hi = b["upper"]["value"] if b.get("upper") else float("inf")
    return max(a_lo, b_lo) <= min(a_hi, b_hi)


def _option_overlap(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    shared = len(set(a) & set(b))
    return shared / min(len(a), len(b))


# ------------------------------------------------------------------------------------ field agreement

def compare(golden: dict, produced: dict) -> dict:
    """The seven fields, each `True`, `False` or `None` for not-applicable.

    `kind` and `unit` are `None` for a Choice pair (judgement call 2): a choice has no measure, and
    counting the absence as agreement would flatter every Choice belief in the corpus.
    """
    is_interval = golden.get("type") == "INTERVAL" and produced.get("type") == "INTERVAL"
    return {
        "type": golden.get("type") == produced.get("type"),
        "kind": (normalise(golden.get("kind")) == normalise(produced.get("kind")))
        if is_interval else None,
        "unit": (normalise(golden.get("unit")) == normalise(produced.get("unit")))
        if is_interval else None,
        "expected_or_band": _expected_or_band(golden, produced),
        "risk": normalise(golden.get("risk")) == normalise(produced.get("risk")),
        "mark": normalise(golden.get("mark")) == normalise(produced.get("mark")),
        "founder_phrase": normalise(golden.get("founder_phrase"))
        == normalise(produced.get("founder_phrase")),
    }


def _expected_or_band(golden: dict, produced: dict) -> bool:
    """Exact, not fuzzy -- the §8.3 phrase table is a fixture, and close is not applied."""
    if golden.get("type") != produced.get("type"):
        return False
    if golden.get("type") == "CHOICE":
        return normalise(golden.get("expected")) == normalise(produced.get("expected"))
    for end in ("lower", "upper"):
        a, b = golden.get(end), produced.get(end)
        if (a is None) != (b is None):
            return False
        if a is None:
            continue
        if a["value"] != b["value"] or a["inclusive"] != b["inclusive"] \
                or a["exact"] != b["exact"]:
            return False
    return True


def pair_score(fields: dict, golden: dict, produced: dict) -> float:
    """Agreeing fields, plus a heading tie-break worth strictly less than one field."""
    agreed = sum(1 for value in fields.values() if value is True)
    return agreed + 0.5 * _heading_similarity(golden, produced)


def _heading_similarity(golden: dict, produced: dict) -> float:
    a = set(normalise(golden.get("heading")).split())
    b = set(normalise(produced.get("heading")).split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ----------------------------------------------------------------------------------------- matching

def align(goldens: list, produced_beliefs: list) -> Alignment:
    """Greedy maximum over descending pair score, deterministic on every tie.

    Ties are broken by golden id order and then produced index, so two runs of the same inputs give
    byte-identical alignments -- which is what lets a report's numbers be traced to a diff on disk.
    A genuine top-score tie between two goldens for one produced belief is recorded in `ambiguous`
    for the judge (`judge.py`, spec Phase 5) rather than settled here by an arbitrary rule.
    """
    golden_views = [(g, golden_view(g)) for g in goldens]
    produced_views = [(i, produced_view(b)) for i, b in enumerate(produced_beliefs)]

    scored = []
    for gi, (golden, gview) in enumerate(golden_views):
        for pi, pview in produced_views:
            if not is_candidate(gview, pview):
                continue
            fields = compare(gview, pview)
            scored.append((pair_score(fields, gview, pview), gi, pi, fields))

    scored.sort(key=lambda row: (-row[0], row[1], row[2]))

    alignment = Alignment()
    used_golden, used_produced = set(), set()
    best_for_produced = {}
    for score, gi, pi, _fields in scored:
        best_for_produced.setdefault(pi, []).append((score, gi))
    for score, gi, pi, fields in scored:
        if gi in used_golden or pi in used_produced:
            continue
        rivals = [g for s, g in best_for_produced.get(pi, [])
                  if s == score and g != gi and g not in used_golden]
        if rivals:
            alignment.ambiguous.append({
                "produced_index": pi,
                "golden_ids": [golden_views[gi][0].id] + [golden_views[r][0].id for r in rivals],
                "score": score,
            })
        used_golden.add(gi)
        used_produced.add(pi)
        alignment.matched.append(Pair(golden_id=golden_views[gi][0].id, produced_index=pi,
                                      score=score, by="structure", fields=fields))

    alignment.missing = [g.id for gi, (g, _v) in enumerate(golden_views) if gi not in used_golden]
    alignment.extra = [pi for pi, _v in produced_views if pi not in used_produced]
    return alignment


def as_wire(belief) -> dict:
    """A golden belief in the shape a produced one arrives in.

    Only the fields the wire carries: the corpus's own `id`, `stage`, `askedOf`, `selection` and
    `group` are the corpus's bookkeeping, not the contract's. Used by the fixed-point test -- a
    matcher that cannot recognise the golden set as itself cannot be trusted to score a model's --
    and by the report, to show a golden beside a produced one in one shape.
    """
    wire = {
        "heading": belief.heading,
        "statement": belief.statement,
        "risk": belief.risk,
        "mark": belief.mark,
        "expectation": belief.expectation,
    }
    if belief.founder_phrase is not None:
        wire["founderPhrase"] = belief.founder_phrase
    return wire
