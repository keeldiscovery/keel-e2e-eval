"""The Overview a founder reads, drawn from one `BriefFacts` (spec 052 FR-3; keel-cloud 104, keel-web 077 FR-2;
design `report-and-follow-up-design-2026-10-17.md` §3, §4.1).

keel-web 077 composes no card line (the cloud's §3 table is the one source): every number and line on the Overview is
the wire's, and what the page adds is its chrome -- the verdict's words, the why line's joiners, the tiles' frames,
the panels' lead lines and the foot. This module states that chrome **once** and draws the whole Overview from a
`BriefFacts` (and, for the too-few lead's count, each dimension's `n`), so the same drawing serves two readers:

- **`report_overview` at zero spend** (`DRY=1`, `instructions/marks.py` call 117): the Overview drawn from keel-cloud's
  own facts for a corpus entry (`BriefFactsCorpusTest`, `build/brief-facts/<entry>.json`) against the Overview drawn
  from this repository's reading of the same entry (`brief_facts.facts_for`) -- one check a hero, a tile, a panel and
  the foot (`compare`);
- **`report_overview` on a journey** (`evals/report_marks.py`): the Overview drawn from the wire's `StandingsView`
  against the page keel-web drew.

The words marked *as 077 defines* are the spec's (keel-web `specs/077-report/spec.md` FR-2) where 077 had not yet
been built when this was written (2026-10-17); the journey pass holds them to what 077 built.
"""

from __future__ import annotations

import re

from .brief_facts import BROKE_ON, VERDICT_WORDS, FactsCompare

VECTORS = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# --------------------------------------------------------------------------- 077's chrome (as 077 defines)

#: keel-web `BRIEF_DECISION_WORDS`.
DECISION_WORDS = {"BUILD": "Build", "BUILD_BUT_CHANGE": "Build, but change it", "NOT_YET": "Not yet",
                  "KEEP_INTERVIEWING": "Keep interviewing"}
#: keel-web `BRIEF_HOW_SURE_WORDS`, capitalised as the why line opens with it (*Fairly sure.*).
HOW_SURE_WORDS = {"LOW": "Low", "MEDIUM": "Medium", "FAIRLY_SURE": "Fairly sure"}
#: keel-web `STAGE_LABEL`: the panels' names and the ship's caption.
STAGE_NAME = {"PROBLEM": "The problem", "SOLUTION": "Your solution", "COMMERCIAL": "Will they pay"}
SHOULD_YOU_BUILD_IT = "Should you build it?"
EVERY_DIMENSION_HOLDS = "Every dimension holds."
CARD_NEEDS = "A card needs 5 to say anything and 10 to be sure."
SEND_TO_MORE = "Send the questions to more people ›"
PILOT_TILE_LABEL = "Pilot"
PILOT_NONE_YET = "None yet"
PILOT_FILLS = "fills as people finish"
PRICE_TILE_LABEL = "What they would pay"
PRICE_NOT_ASKED = "Not asked yet"
PRICE_NOT_ASKED_LINE = "no decision-maker has answered the money questions"
NOBODY_YET = "nobody has answered this yet"
NOT_ASKED_LEAD = "Nobody has answered the money questions yet."
EVERY_ROW_OPENS = "Every row opens its stage page, with every answer named."
#: The deck keel-web 077 deleted (design §4.1 *Gone from today's deck*): none of these may come back.
OLD_DECK_WORDS = ("A band opens its stage", "Every band opens its stage page", "Nothing to download yet")
#: Cards whose statuses make the Insights view's *Nothing to read into yet* (with KEEP_INTERVIEWING; design §4.2).
THIN = ("TOO_FEW_TO_CALL", "NOT_ASKED_YET")


def too_few_lead(n) -> str:
    return f"Too few to call: {n} answered, 5 are needed."


def eyebrow(n) -> str:
    return f"Overview · locked · {n} answered"


def people_answered(n) -> str:
    return f"{n} {'person has' if n == 1 else 'people have'} answered."


def pilot_signed_up(opted, finished) -> str:
    return f"{opted} of {finished} signed up"


def pilot_link_line(per_link) -> str:
    """keel-web `pilotLinkLine`: *2 of 12 people who have it · 0 of 8 decision-makers* (the served words)."""
    return " · ".join(f"{p.get('optedIn')} of {p.get('finished')} {p.get('words')}" for p in per_link or [])


def people_by_link(per_link) -> str:
    """keel-web `peopleByLink`: *15 people who have it · 12 decision-makers*."""
    return " · ".join(f"{p.get('finished')} {p.get('words')}" for p in per_link or [])


def price_tile_line(chose, n) -> str:
    return f"half or more said so · {chose} of {n} decision-makers"


def head(words) -> str:
    """A status's verdict half (`statusWords` before its ` · `)."""
    return str(words or "").split(" · ", 1)[0]


def _lower(text: str) -> str:
    text = str(text or "")
    return text[:1].lower() + text[1:]


def stage_of(key: str) -> str:
    return str(key).split(".", 1)[0].upper()


# ------------------------------------------------------------------------------------------- the drawing

def card_words(card: dict) -> str:
    """A row's card: the number and the line; with no number a left-out card's served line (keel-web 077 call 8), else
    *nobody has answered this yet*."""
    number = card.get("number")
    if number:
        return f"{number} {card.get('line')}"
    # keel-cloud 126 FR-6c: a derived Ability card carries its count inside the line and no number ("the price is
    # below what it costs them today for 6 of 7"); a card with a real status draws its line, only one with none draws
    # *nobody has answered this yet*
    if card.get("status") == "LEFT_OUT" or (card.get("line") and card.get("status") not in (None, "NOT_ASKED_YET")):
        return card.get("line")
    return NOBODY_YET


def tiles(facts: dict, price_median: dict | None) -> dict:
    pilot = facts.get("pilot") or {}
    if int(pilot.get("finished") or 0) == 0:
        pilot_tile = [PILOT_TILE_LABEL, PILOT_NONE_YET, PILOT_FILLS]
    else:
        pilot_tile = [PILOT_TILE_LABEL, pilot_signed_up(pilot.get("optedIn"), pilot.get("finished")),
                      f"{pilot.get('percent')}% · {pilot_link_line(pilot.get('perLink'))}"]
    if price_median:
        price_tile = [PRICE_TILE_LABEL, f"{price_median.get('edgeSaid')} or more",
                      price_tile_line(price_median.get("chose"), price_median.get("n"))]
    else:
        price_tile = [PRICE_TILE_LABEL, PRICE_NOT_ASKED, PRICE_NOT_ASKED_LINE]
    return {"pilot": pilot_tile, "price": price_tile}


def failing(facts: dict) -> list:
    return [c for c in facts.get("cards") or [] if c.get("status") in BROKE_ON]


def hero(facts: dict) -> dict:
    decision = facts.get("decision") or {}
    label = decision.get("label")
    n = int((facts.get("pilot") or {}).get("finished") or 0)
    if label == "KEEP_INTERVIEWING":
        why = [people_answered(n), CARD_NEEDS, SEND_TO_MORE]
    else:
        # spec 064 FR-8 / 8c (keel-cloud 122 FR-3, keel-web 098 FR-2): the reason line, then the decision's named change
        # -- `decision.change.sentence` and, where a second line broke, `change.also.sentence` -- in place of the
        # semicolon list of the failing cards this module used to join ("{Dimension} is {status}; ..."), deleted
        why = [f"{HOW_SURE_WORDS.get(decision.get('howSure'), decision.get('howSure'))}.", decision.get("reason")]
        change = decision.get("change") or {}
        why += [x for x in (change.get("sentence"), (change.get("also") or {}).get("sentence")) if x]
        if label == "BUILD" or (not change and not failing(facts)):
            why.append(EVERY_DIMENSION_HOLDS)
    return {"kicker": SHOULD_YOU_BUILD_IT, "label": label, "verdict": DECISION_WORDS.get(label, label),
            "why": why, "send_more": label == "KEEP_INTERVIEWING",
            "caption": [STAGE_NAME[v] for v in VECTORS]}


def panels(facts: dict, n_of: dict | None = None, served: dict | None = None) -> dict:
    """The three panels in `VECTORS` order: name, pill, lead lines, one row a card in the facts' (registry) order.
    `served` is the wire's own vector counts where the page reads them (keel-web 077 `panelLeadOf`: *k of n holding.*
    is `dimensionsHolding` of `dimensionsTotal`, the too-few lead `peopleAnswered`); without it (the DRY compare) the
    lead counts the facts' cards and the dimensions' `n`."""
    n_of = n_of or {}
    served = served or {}
    verdicts = {v.get("vector"): v.get("verdict") for v in facts.get("vectors") or []}
    out = {}
    for vector in VECTORS:
        cards = [c for c in facts.get("cards") or [] if stage_of(c.get("key")) == vector]
        verdict = verdicts.get(vector)
        mine = served.get(vector) or {}
        holding = mine.get("dimensionsHolding", sum(1 for c in cards if c.get("status") == "HOLDING_UP"))
        total = mine.get("dimensionsTotal", holding)
        failing_cards = [c for c in cards if c.get("status") in BROKE_ON]
        if verdict in BROKE_ON and failing_cards:
            lead = [f"{c.get('name')} · {' '.join(x for x in (c.get('number'), c.get('line')) if x)}"
                    for c in failing_cards]
        elif verdict == "TOO_FEW_TO_CALL":
            if "peopleAnswered" in mine:
                answered = mine["peopleAnswered"]
            else:
                thin = [n_of.get(c.get("key")) for c in cards if c.get("status") == "TOO_FEW_TO_CALL"]
                answered = min([x for x in thin if x is not None] or [0])
            lead = [too_few_lead(answered)]
        elif verdict in ("NOT_ASKED_YET", "NOT_TESTED"):
            lead = [NOT_ASKED_LEAD]
        else:
            lead = [f"{holding} of {total} holding."]
        out[vector] = {"name": STAGE_NAME[vector], "pill": VERDICT_WORDS.get(verdict, verdict), "lead": lead,
                       "rows": [{"key": c.get("key"), "parts": [c.get("name"), head(c.get("statusWords")),
                                                                card_words(c)],
                                 "href": f"/s/{vector}#{c.get('key')}"} for c in cards]}
    return out


def overview(facts: dict, *, price_median=None, n_of: dict | None = None, use_facts_median: bool = True,
             served: dict | None = None, answered: int | None = None) -> dict:
    """The whole Overview from one `BriefFacts`. `price_median` defaults to `facts.commercial.priceMedian` (keel-cloud
    104 serves it there and at `StandingsView.priceMedian`, equal); `n_of` is each dimension's `n`, the too-few lead's
    count."""
    if price_median is None and use_facts_median:
        price_median = (facts.get("commercial") or {}).get("priceMedian")
    pilot = facts.get("pilot") or {}
    # keel-web 102 FR-3a: the eyebrow and the foot count every answer (`StandingsView.people.answered`; a gate No is an
    # answer); the pilot tile keeps 123 FR-4's `finished`. A caller with no people count reads `finished` as before.
    n = int(answered if answered is not None else (pilot.get("finished") or 0))
    return {"eyebrow": eyebrow(n), "hero": hero(facts), "tiles": tiles(facts, price_median),
            "panels": panels(facts, n_of, served),
            "foot": [EVERY_ROW_OPENS, f"{n} answered · {people_by_link(pilot.get('perLink'))}"]}


def parts(drawn: dict) -> list:
    """The Overview as `(part, words)` pairs, one a check: the hero, each tile, each panel, the foot."""
    out = [("hero", drawn["hero"]), ("tile:pilot", drawn["tiles"]["pilot"]), ("tile:price", drawn["tiles"]["price"])]
    out += [(f"panel:{v}", drawn["panels"][v]) for v in VECTORS]
    out.append(("foot", drawn["foot"]))
    return out


# ------------------------------------------------------------------------------------------ reading a page

def norm(text) -> str:
    """Words as a reader compares them: one space, no edge space, the typographic apostrophe as the plain one."""
    return " ".join(str(text or "").replace("’", "'").split())


def in_order(text: str, wanted) -> list:
    """The parts of `wanted` that `text` does not carry in that order (each after the one before) -- [] when all do."""
    hay = norm(text).lower()
    missing, at = [], 0
    for part in wanted:
        needle = norm(part).lower()
        if not needle:
            continue
        found = hay.find(needle, at)
        if found < 0 and " · " in needle:
            # spec 064 FR-7a (keel-web 098 FR-4c): a count shown apart ("· 2 more after a free trial first") is drawn
            # in its own element, so the page's text carries the pieces in order without the separator
            pieces, at2, ok = [q.strip() for q in needle.split(" · ") if q.strip()], at, True
            for piece in pieces:
                f2 = hay.find(piece, at2)
                if f2 < 0:
                    ok = False
                    break
                at2 = f2 + len(piece)
            if ok:
                at = at2
                continue
        if found < 0:
            missing.append(part)
        else:
            at = found + len(needle)
    return missing


# ------------------------------------------------------------------------------------- DRY: the compare

def n_of_entry(entry) -> dict:
    return {k: s.get("n") for k, s in ((entry.expected or {}).get("standings") or {}).items()}


def compare(entry, registry, cloud_facts: dict | None) -> FactsCompare:
    """keel-cloud's facts for one entry drawn as the Overview, against the Overview this repository's reading draws:
    one check a hero, a tile, a panel and the foot (seven an entry)."""
    from . import brief_facts                                          # noqa: PLC0415
    score = FactsCompare(entry.id)
    if not isinstance(cloud_facts, dict):
        score.measured = False
        score.reason = f"keel-cloud wrote no brief facts for {entry.id}"
        return score
    n_of = n_of_entry(entry)
    mine = dict(parts(overview(brief_facts.facts_for(entry, registry), n_of=n_of)))
    theirs = dict(parts(overview(cloud_facts, n_of=n_of)))
    for key, want in mine.items():
        score.checks += 1
        if theirs.get(key) == want:
            score.agreed += 1
        else:
            score.mismatches.append({"key": key, "expected": want, "produced": theirs.get(key)})
    return score


def unmeasured(entry_id: str, reason: str) -> FactsCompare:
    score = FactsCompare(entry_id)
    score.measured = False
    score.reason = reason
    return score


#: `report_no_repeat`'s literal patterns (design D6), shared with `evals/report_marks.py`.
NO_REPEAT_PATTERNS = (re.compile(r"\b\d+ of \d+\b"), re.compile(r"[£$€¥]\s?\d"), re.compile(r"\b\d+ months? out of\b"))
