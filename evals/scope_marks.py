"""The study-scope marks (spec 071 FR-2 / FR-3; keel-cloud 133, contract 38; keel-web 109): SC1-SC8, scored at the end
of S-015 (the problem study) and S-016 (money alone) from the record `evals/scope_journey.py` keeps.

A journey ruler, like `contacts_marks` and `guide_marks`: versioned on its own (`SCOPE_MARKS_VERSION`), never a row of
the instruction eval's `judge()`, and `MARKS_VERSION` (20) does not move. Every mark is deterministic and measured on
what the screens drew and the wire served:

* **SC1 choose** -- the scope's card picked on *What do you want to validate?*, the plan card's scope, badge and lines
  keel-web 109's own, the create request carrying the scope and the project serving it;
* **SC2 corridor** -- every founder screen's kicker counts the scope's steps (*Step k of 3* / *of 5*), money alone's
  step 3 is *Your idea*, and step 5's counter counts its screens -- since keel-web 113 FR-2 hid *A word from you*, two
  (the pilot, who asks) and none in the problem study, whose last step is who asks alone (v2, spec 073 FR-2);
* **SC3 links** -- the links the scope issues: one kind (the person with the problem in the problem study; the
  decision-maker alone on B2B money alone);
* **SC4 interview** -- what each link served and drew: the problem study's gate (counted) + story + part 1 and the
  thank-you with no pilot box; money alone's decision-maker's link opening with the problem in one spoken sentence,
  then the idea card, then part 3 and no gate;
* **SC5 standings** -- the scope's vectors alone on the wire (none NOT_TESTED, the others absent), the served question,
  the ship's pieces and no gate fact;
* **SC6 decision** -- the decision's label by keel-cloud 133 FR-7's rule over the served verdicts, drawn in its words;
* **SC7 overview** -- the Overview as drawn: the question, one card, the one-piece ship, the tiles (none in the problem
  study; Pilot and *What they would pay* where the money is) and the tabs (no Pilot tab in the problem study);
* **SC8 the money link screens** (v3, spec 100; keel-cloud 166, keel-web 145) -- on money alone's person link (FULL,
  no gate) `Interview.condition` is served as the mirror asks it (`vectors_script.money_condition`) where the context
  carries a condition, and none where it carries none; the link opens on the screener (or on the reveal with none)
  and a person who answers it outside draws the screener alone. Where the gate is served the link's own `condition`
  is absent (the gate carries the chip). B2B money alone issues no person's link: met, and says why.
"""

from __future__ import annotations

import re

from instructions import corpus as corpus_mod
from instructions import spoken

#: v1 (spec 071): SC1-SC7 born. v2 (spec 073 FR-2, keel-web 113 FR-2): SC2 re-pinned -- step 5 counts two screens
#: (*1 of 2*, *2 of 2*: the pilot, who asks; the word hidden) and the problem study's who asks alone draws no counter
#: (was three, and two in the problem study). v3 (spec 100; keel-cloud 166, keel-web 145): SC8 born, and SC4 reads money
#: alone's person link (FULL) by its `reveal` -- the card that opens it (keel-cloud 133 FR-4) -- where it read `idea`,
#: which only the decision-maker's link serves (spec 101's *what the spec got wrong* 5); a person outside is not held to
#: the card they never reach.
SCOPE_MARKS_VERSION = 3
MARKS = ("SC1", "SC2", "SC3", "SC4", "SC5", "SC6", "SC7", "SC8")

#: keel-cloud 133 FR-1 / keel-web 109 `scopeVectors`.
SCOPE_VECTORS = {"PROBLEM": ("PROBLEM",), "SOLUTION": ("SOLUTION",), "SOLUTION_COMMERCIAL": ("SOLUTION", "COMMERCIAL"),
                 "COMMERCIAL": ("COMMERCIAL",), "ALL": ("PROBLEM", "SOLUTION", "COMMERCIAL")}
#: keel-cloud 133 FR-7 `StandingsView.question`.
QUESTION = {"PROBLEM": "Should you build it?", "SOLUTION": "Does it fit?",
            "SOLUTION_COMMERCIAL": "Does it fit, and will they pay?", "COMMERCIAL": "Will they pay?",
            "ALL": "Should you build it?"}
#: keel-web `BRIEF_DECISION_WORDS`.
DECISION_WORDS = {"BUILD": "Build", "BUILD_BUT_CHANGE": "Build, but change it", "NOT_YET": "Not yet",
                  "KEEP_INTERVIEWING": "Keep interviewing"}
#: keel-web 109 `ScopePlan`: the plan card's lines (the registry's names, design §9).
PLAN_LINES = {"PROBLEM": ["Prevalence", "Frequency", "Importance", "Current solution"],
              "COMMERCIAL": ["Existing sacrifice", "Price", "Ability to pay", "Buyer and payer", "Purchase friction",
                             "Commitment"]}
PLAN_SCOPE = {"PROBLEM": "problem", "SOLUTION": "solution", "SOLUTION_COMMERCIAL": "solution-money",
              "COMMERCIAL": "money"}
BADGE = {"PROBLEM": "Problem", "SOLUTION": "Solution", "SOLUTION_COMMERCIAL": "Solution + money", "COMMERCIAL": "Money"}
#: keel-web 109 `corridorStepsOf`: the steps each scope walks.
STEPS = {"PROBLEM": 3, "SOLUTION": 4, "SOLUTION_COMMERCIAL": 5, "COMMERCIAL": 5, "ALL": 5}
THIN = ("TOO_FEW_TO_CALL", "NOT_ASKED_YET")
#: The kicker as drawn (its capitals are CSS, `.corridor__kicker`, so it is matched with the case ignored).
_KICKER = re.compile(r"^Step (\d) of (\d)\b", re.IGNORECASE)


def decision_by_rule(scope: str, verdicts: dict) -> str:
    """keel-cloud 133 FR-7 (judgement call 2): *Keep interviewing* while the scope's first vector is too few or not asked,
    or any in-scope vector is not tested; then the first vector not holding -> *Not yet* where it is the problem, else
    *Build, but change it*; every in-scope vector holding -> *Build*; else *Build, but change it*."""
    vectors = SCOPE_VECTORS[scope]
    first = verdicts.get(vectors[0])
    if first in THIN or any(verdicts.get(v) in (None, "NOT_TESTED") for v in vectors):
        return "KEEP_INTERVIEWING"
    if first != "HOLDING_UP":
        return "NOT_YET" if vectors[0] == "PROBLEM" else "BUILD_BUT_CHANGE"
    if all(verdicts.get(v) == "HOLDING_UP" for v in vectors):
        return "BUILD"
    return "BUILD_BUT_CHANGE"


def sentence_faults(text: str | None, founder_texts=()) -> list[str]:
    """The spoken-form rules keel-cloud 133 FR-6 holds the problem's sentence to (`ProblemSentence`; the founder's rule
    of 2026-10-23): one sentence, six to `spoken.STEM_MAX_WORDS` (20) words, no M5 word -- since spec 107 (keel-cloud
    175 `ProblemSentence.of(statement, audienceWords, founderTexts)`) none the founder typed (`corpus.founder_texts`,
    `corpus.typed_in`): a statement that keeps Palus's *money market fund* is still said."""
    text = " ".join(str(text or "").split())
    if not text:
        return ["no sentence"]
    faults = []
    words = len(text.split())
    if words > spoken.STEM_MAX_WORDS:
        faults.append(f"{words} words, more than {spoken.STEM_MAX_WORDS}")
    if words < 6:
        faults.append(f"{words} words, under six")
    if not text.endswith((".", "?")) or re.search(r"[.?!;:]\s+\S", text):
        faults.append("not one sentence")
    lowered = text.lower()
    faults += [f"M5 word {w!r}" for w in corpus_mod.M5_WORDS
               if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", lowered) and not corpus_mod.typed_in(w, founder_texts)]
    return faults


def _mark(mark: str, faults: list, measured: bool = True, why: str | None = None) -> dict:
    return {"mark": mark, "measured": measured, "ok": measured and not faults, "faults": faults,
            **({"why": why} if why else {})}


def sc1(record: dict) -> dict:
    scope = record["scope"]
    chose = record.get("choose") or {}
    plan = (chose.get("picked") or {}).get("plan") or {}
    faults = []
    if plan.get("scope") != PLAN_SCOPE.get(scope):
        faults.append({"plan scope": plan.get("scope"), "want": PLAN_SCOPE.get(scope)})
    if (plan.get("badge") or "").strip() != BADGE.get(scope):
        faults.append({"badge": plan.get("badge"), "want": BADGE.get(scope)})
    if scope in PLAN_LINES and plan.get("lines") != PLAN_LINES[scope]:
        faults.append({"lines": plan.get("lines"), "want": PLAN_LINES[scope]})
    if record.get("created") != scope:
        faults.append({"create request scope": record.get("created"), "want": scope})
    if record.get("served_scope") != scope:
        faults.append({"overview scope": record.get("served_scope"), "want": scope})
    return _mark("SC1", faults)


def sc2(record: dict) -> dict:
    scope = record["scope"]
    faults = []
    kickers = record.get("kickers") or []
    if not kickers:
        faults.append("no corridor kicker read")
    for where, kicker in kickers:
        m = _KICKER.match(kicker or "")
        if not m or int(m.group(2)) != STEPS[scope]:
            faults.append({"screen": where, "kicker": kicker, "want": f"Step k of {STEPS[scope]}"})
    if scope == "COMMERCIAL":
        idea = record.get("idea_kicker") or ""
        if not idea.lower().startswith("step 3 of 5 · your idea"):
            faults.append({"idea kicker": idea, "want": "Step 3 of 5 · Your idea"})
    want = [] if scope == "PROBLEM" else ["1 of 2", "2 of 2"]          # v2: the word hidden (keel-web 113 FR-2)
    if record.get("counters") != want:
        faults.append({"step 5": record.get("counters"), "want": want})
    return _mark("SC2", faults)


#: keel-cloud 133 FR-5: the uncounted gate's fact line in the solution studies alone.
GATE_FACT = ("SOLUTION", "SOLUTION_COMMERCIAL")


def links_of(scope: str, b2b: bool) -> set:
    """keel-cloud 133 FR-4: the kinds of link a scope issues -- the person's (FULL) wherever anyone with the problem is
    asked (not on B2B money alone), the decision-maker's (COMMERCIAL_LINK) on a B2B study with the money in scope."""
    out = set()
    if not (scope == "COMMERCIAL" and b2b):
        out.add("FULL")
    if b2b and "COMMERCIAL" in SCOPE_VECTORS[scope]:
        out.add("COMMERCIAL_LINK")
    return out


def sc3(record: dict) -> dict:
    scope, b2b = record["scope"], record.get("b2b")
    want = links_of(scope, bool(b2b))
    kinds = set(record.get("kinds") or [])
    faults = [] if kinds == want and record.get("links") == record.get("people") else [
        {"kinds": sorted(kinds), "want": sorted(want), "links": record.get("links"), "people": record.get("people")}]
    return _mark("SC3", faults)


def sc4(record: dict) -> dict:
    scope = record["scope"]
    faults = []
    for person, iv in (record.get("interviews") or {}).items():
        parts = [p.get("part") for p in iv.get("parts") or []]
        gate = iv.get("gate")
        kickers = [i.get("kicker") for p in iv.get("parts") or [] for i in p.get("items") or []]
        if scope == "PROBLEM":
            if gate is None or gate.get("counts") is False:
                faults.append({person: "no counted gate", "gate": gate})
            if parts and parts != [1]:
                faults.append({person: "parts", "served": parts, "want": [1]})
            if any(not str(k or "").startswith("Part 1 of 1") for k in kickers):
                faults.append({person: "kickers", "served": kickers})
            if (iv.get("done") or {}).get("pilot"):
                faults.append({person: "a pilot box served", "done": iv.get("done")})
            if (record.get("pilot_boxes") or {}).get(person):
                faults.append({person: "a pilot box drawn"})
            if not (record.get("done") or {}).get(person):
                faults.append({person: "no thank-you drawn"})
        if scope == "COMMERCIAL":
            # v3 (spec 100): the person's link (FULL) opens with the reveal, the decision-maker's with the idea card
            idea = (iv.get("reveal") if iv.get("kind") == "FULL" else iv.get("idea")) or {}
            if gate is not None:
                faults.append({person: "a gate on money alone", "gate": gate})
            if parts != [3]:
                faults.append({person: "parts", "served": parts, "want": [3]})
            # the decision-maker's link keeps its own kicker, *The buying decision · k of 6* (as under ALL)
            if [str(k or "").rsplit("· ", 1)[-1] for k in kickers] != [f"{n} of {len(kickers)}"
                                                                     for n in range(1, len(kickers) + 1)]:
                faults.append({person: "kickers", "served": kickers})
            said = sentence_faults(idea.get("problem"), record.get("founder_texts") or ())
            if said:
                faults.append({person: "the problem's sentence", "served": idea.get("problem"), "faults": said})
            if record.get("problem_sentence") and idea.get("problem") != record["problem_sentence"]:
                faults.append({person: "the problem's sentence", "served": idea.get("problem"),
                               "want": record["problem_sentence"]})
            drawn = (record.get("idea_screens") or {}).get(person) or {}
            if person in (record.get("outside") or ()):
                continue                     # v3: outside, the screener ended the link before the card
            if drawn.get("problem") != idea.get("problem") or not drawn.get("card"):
                faults.append({person: "the idea screen", "drawn": drawn, "served": idea.get("problem")})
    if not record.get("interviews"):
        faults.append("no interview served")
    return _mark("SC4", faults)


def sc5(record: dict) -> dict:
    scope = record["scope"]
    standings = record.get("standings") or {}
    vectors = [v.get("vector") for v in standings.get("vectors") or []]
    faults = []
    if vectors != list(SCOPE_VECTORS[scope]):
        faults.append({"vectors": vectors, "want": list(SCOPE_VECTORS[scope])})
    if any(v.get("verdict") == "NOT_TESTED" for v in standings.get("vectors") or []):
        faults.append("a vector NOT_TESTED")
    served = (standings.get("facts") or {}).get("vectors") or {}
    facts = {v.get("vector") for v in served} if isinstance(served, list) else set(served)
    if facts - set(SCOPE_VECTORS[scope]):
        faults.append({"facts.vectors": sorted(facts)})
    if standings.get("scope") != scope:
        faults.append({"scope": standings.get("scope"), "want": scope})
    if standings.get("question") != QUESTION[scope]:
        faults.append({"question": standings.get("question"), "want": QUESTION[scope]})
    verdicts = {v.get("vector"): v.get("verdict") for v in standings.get("vectors") or []}
    ship = [(p.get("vector"), p.get("verdict")) for p in standings.get("ship") or []]
    if ship != [(v, verdicts.get(v)) for v in SCOPE_VECTORS[scope]]:
        faults.append({"ship": standings.get("ship"), "want": list(SCOPE_VECTORS[scope])})
    if bool(standings.get("gateFact")) != (scope in GATE_FACT):
        faults.append({"gateFact": standings.get("gateFact"), "want": "a fact line" if scope in GATE_FACT else None})
    return _mark("SC5", faults)


def sc6(record: dict) -> dict:
    scope = record["scope"]
    standings = record.get("standings") or {}
    verdicts = {v.get("vector"): v.get("verdict") for v in standings.get("vectors") or []}
    want = decision_by_rule(scope, verdicts)
    label = (((standings.get("facts") or {}).get("decision")) or {}).get("label")
    drawn = (record.get("overview") or {}).get("verdict") or {}
    faults = []
    if label != want:
        faults.append({"served": label, "rule": want, "verdicts": verdicts})
    if drawn.get("label") != label or (drawn.get("text") or "").strip() != DECISION_WORDS.get(label):
        faults.append({"drawn": drawn, "served": label})
    allowed = ("BUILD", "NOT_YET", "KEEP_INTERVIEWING") if scope == "PROBLEM" else \
        ("BUILD", "BUILD_BUT_CHANGE", "KEEP_INTERVIEWING")
    if label not in allowed:
        faults.append({"served": label, "the scope's words": allowed})
    return _mark("SC6", faults)


def sc7(record: dict) -> dict:
    scope = record["scope"]
    seen = record.get("overview") or {}
    vectors = list(SCOPE_VECTORS[scope])
    faults = []
    if seen.get("question") != QUESTION[scope]:
        faults.append({"question": seen.get("question"), "want": QUESTION[scope]})
    if seen.get("panels") != vectors:
        faults.append({"cards": seen.get("panels"), "want": vectors})
    piece = {1: "rp-stages--one", 2: "rp-stages--two"}.get(len(vectors))
    if piece and piece not in (seen.get("stages_class") or ""):
        faults.append({"stages": seen.get("stages_class"), "want": piece})
    if seen.get("ship") != vectors:
        faults.append({"ship": seen.get("ship"), "want": vectors})
    tiles = seen.get("tiles") or {}
    tabs = seen.get("tabs") or []
    if scope == "PROBLEM":
        if tiles.get("present"):
            faults.append({"tiles": tiles, "want": "none"})
        if "pilot" in tabs:
            faults.append({"tabs": tabs, "want": "no Pilot tab"})
    else:
        want = ["pilot", "price"] if "COMMERCIAL" in vectors else ["pilot"]
        one = len(want) == 1
        if tiles.get("names") != want or ("rp-tiles--one" in (tiles.get("class") or "")) != one:
            faults.append({"tiles": tiles, "want": want})
        if "pilot" not in tabs:
            faults.append({"tabs": tabs, "want": "a Pilot tab"})
    if bool(seen.get("gatefact")) != (scope in GATE_FACT):
        faults.append({"gate fact": seen.get("gatefact"), "want": "drawn" if scope in GATE_FACT else None})
    elif seen.get("gatefact") and seen.get("gatefact") != (record.get("standings") or {}).get("gateFact"):
        faults.append({"gate fact": seen.get("gatefact"), "served": (record.get("standings") or {}).get("gateFact")})
    return _mark("SC7", faults)


def sc8(record: dict) -> dict:
    """v3 (spec 100; keel-cloud 166 FR-1, keel-web 145 FR-1): the money link screens."""
    scope = record["scope"]
    interviews = record.get("interviews") or {}
    screens = record.get("screens") or {}
    outside = set(record.get("outside") or ())
    faults: list = []
    if scope == "COMMERCIAL":
        full = {p: iv for p, iv in interviews.items() if iv.get("kind") == "FULL"}
        if not full:
            return _mark("SC8", [], why="no person's link on B2B money alone (keel-cloud 133 FR-4): the decision-maker's "
                                        "screener is spec 076's")
        want = record.get("money_condition")
        for person, iv in full.items():
            if iv.get("gate") is not None:
                faults.append({person: "a gate on money alone", "gate": iv.get("gate")})
            if (iv.get("condition") or None) != want:
                faults.append({person: "condition", "served": iv.get("condition"), "want": want})
            drawn = screens.get(person)
            if drawn is None:
                continue                     # not walked (spec 102): no screen to read
            first = drawn[:1]
            if first != (["condition"] if want else ["reveal"]):
                faults.append({person: "the first screen", "drawn": drawn[:2], "want": "condition" if want else "reveal"})
            if person in outside and drawn != ["condition"]:
                faults.append({person: "outside: the screener alone", "drawn": drawn})
    else:
        for person, iv in interviews.items():
            if iv.get("kind") == "FULL" and iv.get("gate") and iv.get("condition"):
                faults.append({person: "a link condition beside the gate", "served": iv.get("condition")})
    return _mark("SC8", faults)


def score(record: dict) -> dict:
    """The eight marks over one scoped journey's record, every one measured."""
    checks = [f(record) for f in (sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8)]
    return {"version": SCOPE_MARKS_VERSION, "scope": record.get("scope"), "checks": checks,
            "met": sum(1 for c in checks if c["ok"]), "of": len(checks)}
