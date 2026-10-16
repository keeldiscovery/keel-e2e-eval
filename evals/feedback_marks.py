"""The founder's feedback marks (spec 046): keel-cloud 097's and keel-web 070's rules from the founder's staging walk
of 2026-10-15 (screenshots of 2026-10-16), held over one journey's record -- deterministic, zero spend, the shape of
`evals/interviewer_marks.py` (one check a rule; a mark whose subject the record does not carry is **unmeasured** --
reported, never passed).

A **journey** ruler with its own version: no model turn moved in a way the instruction eval measures (097 put the
list rule into `founder-lists.md` -- a subject change, which earns a screen on the founder's word, not a ruler
change), so `instructions/marks.py`'s `MARKS_VERSION` stays where it is.

The journey (`evals/corpus_scenario.py`) builds the record from what the wire answered and what the screens drew;
`score` reads only the record, so a unit test can seed a bad one and watch the mark fail
(`tests/test_feedback_marks.py`).

- **FM1** no calibration list item names a role or a person the founder did not name: `common.role_words` (keel-cloud
  097's registry export, the same list its `L6` refuses on) against the founder's own words -- the four context
  fields, the two seeds, the persona's roles and that dimension's Answer (judgement call 2: L6's allow-list also takes
  the confirmed mechanism card and the other saved lists; the eval holds the words the founder typed).
- **FM2** Importance is the own item plus exactly the difficulties the founder's Answer named: Keel's first draft is
  the own item alone, the redraft from the Answer adds those and none other.
- **FM3** Keel's base query carries no industry: no `categories` on any kind's base query.
- **FM4** the idea's name is the seed's product name when the seed carries one; else Keel served none, the Check
  screen demanded one (Save refused `IDEA_NAME_REQUIRED` on the wire; on the screen an empty field with its
  placeholder and Save off), and the name stored is the one the journey typed, at most five words.
- **FM5** an AI-interviewer answer advances without a *Next question* step: no press of it, and no `thinking` phase
  longer than a second between a resolved answer and the next clip's `play`.
- **FM6** a value typed into the AI interviewer's field carries `heard` -- the typed text -- with `how` TYPED.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from harness import vectors_script as vs

#: Bumped whenever a mark is born, retired, or reads its record differently.
FEEDBACK_MARKS_VERSION = 1

#: keel-cloud 097 `VectorCalibration.IMPORTANCE_MIN_ITEMS`: Save and the lock need the own item and two others.
IMPORTANCE_MIN_ITEMS = 3
#: keel-cloud `IdeaLines.NAME_MAX_WORDS` (L5).
NAME_MAX_WORDS = 5
#: keel-web 070 F7: the empty name field's placeholder.
NAME_PLACEHOLDER = "Name it in up to five words"
#: keel-web 070 F1: a resolved answer goes on to the next clip at once (the tick shown ~500 ms first).
THINKING_MAX_MS = 1000

IDEA_NAME_REQUIRED = "IDEA_NAME_REQUIRED"
ONE_MORE_NEEDED = "ONE_MORE_NEEDED"


@dataclass(frozen=True)
class Check:
    mark: str
    rule: str
    measured: bool
    ok: bool
    detail: Any = None


# ------------------------------------------------------------------------------------------------ role words

#: keel-cloud 097 `RoleWords`, restated once in `harness/vectors_script.py` (the script's first drafts obey it too).
role_pattern = vs.role_pattern
carries = vs.carries_role
first_unnamed = vs.first_unnamed_role


# ------------------------------------------------------------------------------------------------ the marks

def no_unnamed_role(r: dict) -> tuple[bool, Any]:
    """FM1: no calibration list item -- label, `asked` clause, phrase -- names a role or a person the founder did not
    name (`common.role_words` against the context, the seeds, the persona's roles and that dimension's Answer)."""
    words = list(r["role_words"])
    founder = r["founder_text"]
    base = " ".join(str(v) for v in (founder.get("context") or {}).values()) + " " + " ".join(
        str(founder.get(k) or "") for k in ("problem_seed", "solution_seed")) + " " + " ".join(
        str(x) for x in founder.get("persona_roles") or [])
    found = []
    for listed in r["lists"]:
        own = f"{base} {listed.get('answer') or ''}"
        texts = [("phrase", listed.get("phrase"))]
        for i, item in enumerate(listed.get("items") or []):
            if item.get("fixed"):
                continue                        # Buyer and payer's "Nobody else" is code's and names nobody
            texts += [(f"items[{i}].label", item.get("label")), (f"items[{i}].asked", item.get("asked"))]
        for where, text in texts:
            word = first_unnamed(text, words, own)
            if word:
                found.append({"dimension": listed.get("dimension"), "draft": listed.get("draft"), "where": where,
                              "text": text, "word": word})
    ok = bool(words) and bool(r["lists"]) and not found
    return ok, {"unnamed": found, "lists": len(r["lists"]), "role_words": len(words)}


def importance_is_own_plus_named(r: dict) -> tuple[bool, Any]:
    """FM2: Importance is the own item plus exactly the difficulties the Answer named -- Keel's first draft the own
    item alone, its redraft the own item and those, none invented -- and the list saved is that list."""
    x = r["importance"]
    own = x.get("own")
    named = list(x.get("named") or [])
    first = list(x.get("first_draft") or [])
    redraft = list(x.get("redraft") or [])
    saved = list(x.get("saved") or [])
    invented = [label for label in redraft[1:] if label not in named]
    missing = [label for label in named if label not in redraft[1:]]
    ok = (bool(own) and first == [own] and redraft[:1] == [own] and not invented and not missing
          and len(redraft) == 1 + len(named) and saved == redraft and len(saved) >= IMPORTANCE_MIN_ITEMS)
    return ok, {"own": own, "first draft": first, "named": named, "redraft": redraft, "saved": saved,
                "invented": invented, "missing": missing}


def base_query_has_no_industry(r: dict) -> tuple[bool, Any]:
    """FM3: Keel's base query carries no industry -- no `categories` on any kind's base query (097 F5)."""
    queries = r["base_query"] or {}
    with_industry = {kind: q.get("categories") for kind, q in queries.items() if (q or {}).get("categories")}
    present = {kind: q is not None for kind, q in queries.items()}
    ok = bool(queries) and all(present.values()) and not with_industry
    return ok, {"kinds": sorted(queries), "present": present, "categories": with_industry}


def idea_named_by_the_founder(r: dict) -> tuple[bool, Any]:
    """FM4: the idea's name is the seed's product name when it has one; else Keel served none, Save and approve were
    refused IDEA_NAME_REQUIRED, the Check screen (when walked unnamed) drew an empty field with its placeholder and
    Save off, and the name stored is the one the journey typed, at most five words."""
    x = r["idea"]
    seed_name = x.get("seed_name")
    served = x.get("served")
    stored = x.get("stored")
    typed = x.get("typed")
    if seed_name:
        ok = served == seed_name and stored in (seed_name, x.get("typed_name"))
        return ok, {"seed name": seed_name, "served": served, "stored": stored}
    refusals = x.get("refusals") or {}
    refused = all((v or {}).get("status") == 422 and (v or {}).get("code") == IDEA_NAME_REQUIRED
                  for v in refusals.values()) and {"approve", "empty"} <= set(refusals)
    screen = x.get("screen")
    demanded = screen is None or (screen.get("value") == "" and screen.get("placeholder") == NAME_PLACEHOLDER
                                  and screen.get("save_enabled") is False)
    words = len((typed or "").split())
    ok = (served is None and refused and demanded and bool(typed) and 1 <= words <= NAME_MAX_WORDS
          and stored == x.get("typed_name") and x.get("approved") is True)
    return ok, {"served": served, "refused": refusals, "screen": screen, "typed": typed, "words": words,
                "stored": stored, "typed_name": x.get("typed_name"), "approved": x.get("approved"),
                "named_on": x.get("named_on")}


def advances_without_next(r: dict) -> tuple[bool, Any]:
    """FM5: an AI-interviewer answer advances without a *Next question* step -- no press of it and no `thinking`
    phase longer than a second between a resolved answer and the next clip's `play`."""
    x = r["ai_flow"]
    events = sorted(x.get("events") or [], key=lambda e: e.get("t") or 0)
    spans, start = [], None
    for e in events:
        if e.get("kind") == "phase":
            if e.get("value") == "thinking" and start is None:
                start = e["t"]
            elif e.get("value") != "thinking" and start is not None and e.get("value") != "speaking":
                start = None                     # thinking that ended somewhere other than a clip
        elif e.get("kind") == "play" and start is not None:
            spans.append(round(e["t"] - start))
            start = None
    plays = sum(1 for e in events if e.get("kind") == "play")
    long = [ms for ms in spans if ms > THINKING_MAX_MS]
    ok = x.get("next_presses") == 0 and plays >= 2 and not long
    return ok, {"next presses": x.get("next_presses"), "plays": plays, "thinking spans (ms)": spans, "long": long}


def typed_field_carries_heard(r: dict) -> tuple[bool, Any]:
    """FM6: a value typed into the AI interviewer's number or amount field goes back with `how` TYPED and `heard`
    the typed text (keel-web 070, DRIFT #89 closed)."""
    rows = r["typed_fields"] or []

    def same(heard, typed) -> bool:
        heard, typed = str(heard or "").strip(), str(typed or "").strip()
        if heard == typed:
            return bool(heard)
        try:
            return float(heard.replace(",", "")) == float(typed)
        except ValueError:
            return False
    bad = [x for x in rows if x.get("how") != "TYPED" or not same(x.get("heard"), x.get("typed"))]
    return bool(rows) and not bad, {"typed": rows, "bad": bad}


#: (mark id, the record key it reads, the rule). Order is the journey's.
MARKS: list[tuple[str, str, Callable[[dict], tuple[bool, Any]]]] = [
    ("FM1", "lists", no_unnamed_role),
    ("FM2", "importance", importance_is_own_plus_named),
    ("FM3", "base_query", base_query_has_no_industry),
    ("FM4", "idea", idea_named_by_the_founder),
    ("FM5", "ai_flow", advances_without_next),
    ("FM6", "typed_fields", typed_field_carries_heard),
]


def score(record: dict) -> list[Check]:
    checks = []
    for mark, key, rule in MARKS:
        doc = (rule.__doc__ or "").strip().split("\n")[0]
        if key not in record:
            checks.append(Check(mark, doc, measured=False, ok=False))
            continue
        try:
            ok, detail = rule(record)
        except (KeyError, TypeError, IndexError, ValueError, AttributeError) as broken:
            ok, detail = False, {"record could not be read": repr(broken)}
        checks.append(Check(mark, doc, measured=True, ok=bool(ok), detail=detail))
    return checks


def owed(record: dict) -> list[str]:
    """Every mark whose subject this record carries."""
    return [m for m, key, _ in MARKS if key in record]


def scorecard(record: dict) -> dict:
    checks = score(record)
    measured = [c for c in checks if c.measured]
    return {"version": FEEDBACK_MARKS_VERSION,
            "measured": len(measured), "met": sum(c.ok for c in measured),
            "unmeasured": [c.mark for c in checks if not c.measured],
            "checks": [{"mark": c.mark, "rule": c.rule, "measured": c.measured, "ok": c.ok, "detail": c.detail}
                       for c in checks]}
