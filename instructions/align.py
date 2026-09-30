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

**This module scores the model's RAW answer, and nothing ever applies it.** Traced end to end at
`master` `aa3b584` (spec 025 T001, `MARKS_VERSION` 8 judgement call 27), so that nobody traces it a
second time:

1. `runner.py:388` -- `answer.result = response.get("result")`. The structured output the host CLI
   returned. JSON-schema-validated against keel-cloud's exported contract (`runner.py:385-389`,
   `validator_module.validate_response`) and **applied to nothing**.
2. `run.py:306` -- `score_mod.score_assumptions(case, entry, answer.result, ...)`.
3. `score.py:161-163` -- `produced = result.get("assumptions")`, then `align(goldens, produced, judge)`.
4. `align.produced_view` (below) reads `belief.get("expectation")`; with no expectation it yields
   `type: None`.
5. `align.structural_candidate` (below) returns `False` on `not golden["type"] or golden["type"] !=
   produced["type"]`, and `is_candidate` refuses too -- *an interval is never judged*, so the judge
   is not asked either.

And keel-cloud's validator does not close it: `instructions/validate.py` shells
`./gradlew -q screenContracts --args="validate <batch> <report>"` and `fold_in` reads only
`accepted` and `refusal` -- a verdict, never a resolved `Assumption`.

**So a belief carrying `reads: {stage, line}` and no expectation would never be a candidate, never
align, and `golden_belief_recall` would fall by one line per reference** -- design §6A.8's *"an
alignment-rule change and a real regression, not a rubric question"*. `resolve_reads` below is that
change: it gives a referencing belief the referent's own expectation **before** alignment, out of
the `earlier_lines` this eval itself numbered and sent. `FIELDS`, `produced_view`, `compare` and
`align` are untouched by it -- what changes is that a referencing belief arrives at them whole.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# The fields `score.py` reports separately. `per` joined at MARKS_VERSION 2 (judgement call 12):
# `Measure` is a three-field record and all three decide equality for `V2`, so a belief whose `per`
# differs expects a different number and an answer against it places nowhere.
FIELDS = ("type", "kind", "unit", "per", "expected_or_band", "risk", "mark", "founder_phrase")

# data-model.md §4: two Choices are candidates when their expected options match, or their option
# sets overlap above this. Half the smaller list is the threshold -- enough that "did you recount
# or ring the supplier" and "did you recount, ring the supplier, or let it go" are one question.
OPTION_OVERLAP_THRESHOLD = 0.5


def normalise(text) -> str:
    """Case- and whitespace-normalised, for every string comparison in this module."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def normalise_phrase(text) -> str:
    """A founder's phrase, with the corpus author's own annotations taken off first.

    Twenty-two of the frozen corpus's eighty-eight `founderPhrase` values end in a parenthetical
    written for a human reviewer rather than by the founder — *"scans each delivery on arrival (the
    present-tense half, per §8.1 step 3)"*, *"£40 a month per site (proxied by comparable spend,
    T1–T4 pass)"*. They are notes about the decomposition, not words anybody typed, and **no
    instruction can or should reproduce them**; leaving them in made a quarter of the corpus
    unmatchable on this field for a reason that has nothing to do with the prose being scored.

    The corpus is frozen and this does not touch it (MARKS_VERSION 3, judgement call 15): the
    annotation is stripped **on the golden side, at comparison time**, so the two sides are
    compared as the same kind of thing. Only a trailing parenthetical is removed, and only when
    something is left in front of it.
    """
    stripped = re.sub(r"\s*\([^()]*\)\s*$", "", str(text or "")).strip()
    return normalise(stripped or text)


@dataclass
class Pair:
    golden_id: str
    produced_index: int
    score: float
    by: str
    fields: dict
    #: True when the structure found no overlap at all and only the judge's reading of the two
    #: option lists made this pair possible. Counted apart from `by == "judge"`, which is a *tie*
    #: the judge broke: one is the judge letting a pair exist, the other the judge choosing
    #: between pairs, and a reader discounting a score wants to know which.
    judged_candidacy: bool = False


@dataclass
class Alignment:
    matched: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    extra: list = field(default_factory=list)
    ambiguous: list = field(default_factory=list)

    @property
    def judged(self) -> int:
        """Pairs a model decided outright -- a tie it broke."""
        return sum(1 for pair in self.matched if pair.by == "judge")

    @property
    def judged_candidacy(self) -> int:
        """Pairs that exist only because a model read two option lists as the same answer space."""
        return sum(1 for pair in self.matched if pair.judged_candidacy)


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

def structural_candidate(golden: dict, produced: dict) -> bool:
    """The candidate rule with no opinion in it -- MARKS_VERSION 1's whole rule."""
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


def is_candidate(golden: dict, produced: dict, judge=None) -> bool:
    """The candidate rule: arithmetic for an interval, meaning for a choice.

    **An interval is never judged.** Same stage, same `measure.kind`, and bands that intersect --
    all three are facts, and a model has no opinion to add.

    **A choice is judged when the words do not line up.** Structural overlap is tried first: equal
    expected options, or option sets overlapping above the threshold. Only when that fails is the
    judge asked whether the two lists describe the same answer space, because the corpus's option
    words are one reasonable phrasing and `Q2` binds a belief's list to *its own selection's*, never
    to the corpus's (the founder's decision, 2026-09-06). Without a judge the old rule stands.
    """
    if structural_candidate(golden, produced):
        return True
    if golden.get("type") != "CHOICE" or produced.get("type") != "CHOICE":
        return False                    # an interval is arithmetic; a model has nothing to add
    if judge is None or not judge.available():
        return False
    if not golden.get("options") or not produced.get("options"):
        return False
    return judge.same_answer_space(golden["options"], produced["options"],
                                   context=str(golden.get("heading") or "")[:60])


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

def compare(golden: dict, produced: dict, judge=None) -> dict:
    """The eight fields, each `True`, `False` or `None` for not-applicable.

    `kind`, `unit` and `per` are `None` for a Choice pair (judgement call 2): a choice has no
    measure, and counting the absence as agreement would flatter every Choice belief in the corpus.

    For a Choice pair, `expected_or_band` is a **judged semantic match** since MARKS_VERSION 2
    (judgement call 11): the corpus's option words are one reasonable phrasing, and two authors
    naming the same answer in different registers agree. String equality is still tried first and
    the judge is only asked when it fails, so a run with no judge degrades to the old rule rather
    than to nothing.
    """
    is_interval = golden.get("type") == "INTERVAL" and produced.get("type") == "INTERVAL"
    return {
        "type": golden.get("type") == produced.get("type"),
        "kind": (normalise(golden.get("kind")) == normalise(produced.get("kind")))
        if is_interval else None,
        "unit": (normalise(golden.get("unit")) == normalise(produced.get("unit")))
        if is_interval else None,
        "per": (normalise(golden.get("per")) == normalise(produced.get("per")))
        if is_interval else None,
        "expected_or_band": _expected_or_band(golden, produced, judge),
        "risk": normalise(golden.get("risk")) == normalise(produced.get("risk")),
        "mark": normalise(golden.get("mark")) == normalise(produced.get("mark")),
        "founder_phrase": normalise_phrase(golden.get("founder_phrase"))
        == normalise_phrase(produced.get("founder_phrase")),
    }


def _expected_or_band(golden: dict, produced: dict, judge=None) -> bool:
    """A band is exact; an expected option is read for meaning.

    The band stays exact because the §8.3 phrase table is a fixture, not a judgement -- a band that
    is close did not apply the table. An expected option is the opposite case: it is a word chosen
    to name an answer, and *"a member of staff"* and *"Someone on my team took it in"* are the same
    answer named twice (the founder's decision, 2026-09-06).
    """
    if golden.get("type") != produced.get("type"):
        return False
    if golden.get("type") == "CHOICE":
        if normalise(golden.get("expected")) == normalise(produced.get("expected")):
            return True
        if judge is None or not judge.available():
            return False
        return judge.same_expected_option(golden.get("expected"), produced.get("expected"),
                                          context=str(golden.get("heading") or "")[:60])
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

def align(goldens: list, produced_beliefs: list, judge=None) -> Alignment:
    """Greedy maximum over descending pair score, deterministic on every tie.

    Ties are broken by golden id order and then produced index, so two runs of the same inputs give
    byte-identical alignments -- which is what lets a report's numbers be traced to a diff on disk.
    A genuine top-score tie between two goldens for one produced belief is recorded in `ambiguous`
    and handed to the judge rather than settled here by an arbitrary rule; with no judge it falls
    to golden id order, which is arbitrary but at least repeatable.
    """
    golden_views = [(g, golden_view(g)) for g in goldens]
    produced_views = [(i, produced_view(b)) for i, b in enumerate(produced_beliefs)]

    scored = []
    for gi, (golden, gview) in enumerate(golden_views):
        for pi, pview in produced_views:
            structural = structural_candidate(gview, pview)
            if not structural and not is_candidate(gview, pview, judge):
                continue
            fields = compare(gview, pview, judge)
            scored.append((pair_score(fields, gview, pview), gi, pi, fields, not structural))

    scored.sort(key=lambda row: (-row[0], row[1], row[2]))

    alignment = Alignment()
    used_golden, used_produced = set(), set()
    best_for_produced = {}
    for score, gi, pi, _fields, _judged in scored:
        best_for_produced.setdefault(pi, []).append((score, gi))
    for score, gi, pi, fields, judged_candidacy in scored:
        if gi in used_golden or pi in used_produced:
            continue
        rivals = [g for s, g in best_for_produced.get(pi, [])
                  if s == score and g != gi and g not in used_golden]
        by = "structure"
        if rivals:
            # A genuine tie: two goldens the structure likes equally for one produced belief. This
            # is the one place a model decides a *pair* rather than a field, and it is choosing
            # between equals rather than overruling arithmetic.
            tied = [gi] + rivals
            alignment.ambiguous.append({
                "produced_index": pi,
                "golden_ids": [golden_views[g][0].id for g in tied],
                "score": score,
            })
            if judge is not None and judge.available():
                chosen = judge.pick(str(produced_views[pi][1].get("statement") or ""),
                                    [str(golden_views[g][1].get("statement") or "")
                                     for g in tied])
                if chosen is None:
                    continue                      # the judge says none of them; leave it unmatched
                gi = tied[chosen]
                fields = compare(golden_views[gi][1], produced_views[pi][1], judge)
                by = "judge"
        if gi in used_golden:
            continue
        used_golden.add(gi)
        used_produced.add(pi)
        alignment.matched.append(Pair(golden_id=golden_views[gi][0].id, produced_index=pi,
                                      score=score, by=by, fields=fields,
                                      judged_candidacy=judged_candidacy))

    alignment.missing = [g.id for gi, (g, _v) in enumerate(golden_views) if gi not in used_golden]
    alignment.extra = [pi for pi, _v in produced_views if pi not in used_produced]
    return alignment


# ------------------------------------------------------------- a belief that reads another belief

def resolve_reads(produced: list, earlier: list) -> tuple:
    """`(beliefs, unresolved)` -- every produced belief, with a resolved `reads` given its referent's
    whole expectation, and the count of references that could not be resolved.

    This is `ScreenResultApplier`'s step 2 of design §6A.5, done here **because nothing does it
    here**: see the module docstring. It is deliberately not a module named for the applier
    (`runs/DRIFT.md` #33/#36/#41/#44/#45, five times the same lesson: this repo keeps no copy of the
    cloud's arithmetic). It is not the server's resolution at all -- the server resolves against
    beliefs on a live aggregate; this resolves against `earlier`, the list **this repository built,
    numbered and sent in the context of that very case** (`context.earlier_lines`). It is the eval
    reading its own homework, which is what an aligner does, and it belongs beside `produced_view`
    because it is the last thing that happens to a produced belief before it is one.

    **Only the expectation is copied.** `risk`, `mark`, `founderPhrase`, `heading` and `statement`
    stay the referencing belief's own, because they are its own claim about its own stage.

    **Four references are not resolved**, each counted and each left to fail to match -- production
    gives a derivation failure one repair turn and this eval has never had one:

    - an ordinal out of range, or naming a stage that is not in `earlier` at all;
    - a `reads` that is not `{stage, line}` -- a shape the contract does not state;
    - a **chain**: the referent must **own** its expectation (design §6A.5 step 4). A line that
      carries a `reads` of its own, or that carries neither a `measure` nor an `options` list, is
      not a referent -- one indirection too many, and the second belief could have named the first.
      It cannot arise off this eval's own `earlier_lines`, which are built from golden beliefs that
      each own their measurement; the rule is here because the contract states it and a list this
      module is *handed* is not a list it wrote.
    - **both at once**: a belief carrying `reads` *and* an expectation keeps its own and is counted
      here anyway, because design §6A.5 says *"Both, or neither, is a shape refusal"* and a shape
      the contract refuses is not a reference that worked.

    The input list is never mutated: a resolved belief is a shallow copy with `expectation` added.
    """
    by_handle = {}
    for line in earlier or []:
        if isinstance(line, dict) and line.get("stage") is not None and line.get("line") is not None:
            by_handle[(str(line["stage"]), line["line"])] = line

    beliefs, unresolved = [], 0
    for belief in produced or []:
        if not isinstance(belief, dict) or not isinstance(belief.get("reads"), dict):
            beliefs.append(belief)
            continue
        reads = belief["reads"]
        handle = (str(reads.get("stage")), reads.get("line"))
        line = by_handle.get(handle)
        own = belief.get("expectation")
        if line is None or (isinstance(own, dict) and own) or not _owns_its_measurement(line):
            # Out of range, a stage that is not an earlier one, a both-at-once shape, or a chain
            # -- one reason each, and the belief goes to the aligner exactly as it arrived.
            unresolved += 1
            beliefs.append(belief)
            continue
        resolved = dict(belief)
        resolved["expectation"] = _expectation_of(line)
        beliefs.append(resolved)
    return beliefs, unresolved


def _owns_its_measurement(line: dict) -> bool:
    """Whether an `earlier_lines` entry is a referent at all: it carries its own band, and it does
    not itself read somebody else's (design §6A.5 step 4)."""
    if line.get("reads") is not None:
        return False
    band = line.get("band") if isinstance(line.get("band"), dict) else None
    if band is None:
        return False
    return isinstance(line.get("measure"), dict) or isinstance(band.get("options"), list)


def _expectation_of(line: dict) -> dict:
    """The referent's whole expectation, out of `earlier_lines`' `measure` and `band` -- the
    `Measure`, the `Bound`s, or the `options` and `expected`, and nothing else."""
    band = line.get("band") if isinstance(line.get("band"), dict) else {}
    measure = line.get("measure")
    if isinstance(measure, dict):
        return {"type": "INTERVAL", "measure": dict(measure),
                "lower": band.get("lower"), "upper": band.get("upper")}
    return {"type": "CHOICE", "options": list(band.get("options") or []),
            "expected": band.get("expected")}


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
