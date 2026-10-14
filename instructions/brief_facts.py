"""The eval's own reading of a corpus entry's `BriefFacts` -- the cards, the pilot, the decision, what broke -- and
its DRY compare against keel-cloud's (spec 040 FR-006; keel-cloud 089 FR-001, FR-002, FR-005, FR-006; judgement
calls 82-84).

keel-cloud assembles `BriefFacts` from a project's stored answers by `StandingsAssembler` and `BriefFacts.of`, and its
`BriefFactsCorpusTest` writes each corpus entry's whole facts (`build/brief-facts/<entry>.json`,
`instructions/cloud_corpus.py`). This module reads the same entry the other way round -- from its
`expected.standings`, `expected.vector_verdicts`, the founder's lists and each answer's `pilot_opt_in`, by the words
design §7.2 and keel-cloud 089 state -- and `compare` holds keel-cloud's to it:

- **marked** (`brief_facts`, one check a card and one the pilot): every card's `key`, `name`, `number`, `line`,
  `status`, `keelBar` (keel-cloud 091 FR-F1: Keel's bar on Importance and Current solution, absent elsewhere and on a
  left-out card; spec 042 call 114) and the verdict half of its `statusWords`; the pilot's `optedIn`, `finished`,
  `percent` and `perLink`;
- **reported, never marked** (call 3): the insight half of `statusWords` (spec 082's words, keel-cloud's own), the
  decision, the vector words, each stage's `broke` key and `notAsked` keys.

The arithmetic here is the corpus's own counts restated, never the engine's: `n`, `inside`, `own_item_picks`,
`optionCounts`, `median` and `yes` are read off the standings the checker and `GoldenCorpusTest` pin; nothing is
recounted from the picks but the pilot, which no standing carries.

`facts_for` is the same reading in `BriefFacts`' shape, the `BRIEF` case's facts when keel-cloud's are not to hand
(the unit fixtures); a run hands the case keel-cloud's own (call 84).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from . import corpus as corpus_mod
from .registry import (ABILITY_KEY, ADOPTION_KEY, BUYER_KEY, COMMITMENT_KEY, COMPATIBILITY_KEY,
                       CURRENT_SOLUTION_KEY, FREQUENCY_KEY, GATE_KEY, IMPORTANCE_KEY, LINK_B2B, LINK_PRIMARY,
                       PRICE_KEY, PURCHASE_FRICTION_KEY, SACRIFICE_KEY, VECTORS)

VERDICT_WORDS = {
    "HOLDING_UP": "Holding up", "NOT_HOLDING_UP": "Not holding up",
    "PEOPLE_DISAGREE": "People disagree", "TOO_FEW_TO_CALL": "Too few to call",
    "NOT_ASKED_YET": "Not asked yet", "LEFT_OUT": "Left out", "NOT_TESTED": "Not tested",
}
CURRENCY_SYMBOL = {"GBP": "£", "USD": "$", "EUR": "€", "JPY": "¥"}
_THIN = ("TOO_FEW_TO_CALL", "NOT_ASKED_YET")
#: keel-cloud 089 FR-002: a stage broke on a called failure only (its call 10).
BROKE_ON = ("NOT_HOLDING_UP", "PEOPLE_DISAGREE")
#: The header's link words (089 call 3).
LINK_WORDS = {LINK_PRIMARY: "people who have it", LINK_B2B: "decision-makers"}
LEFT_OUT_LINE = "you weren't sure, so it was left out"
NOBODY_LINE = "nobody has answered yet"
#: keel-cloud 091 FR-F3: one house style -- a lower-case fragment, the cause, then ", so it was not asked".
NOT_ASKED_WHY = {ABILITY_KEY: "it is derived from what they lose today and your price, so it was not asked",
                 PURCHASE_FRICTION_KEY: "a person, not a business, buys it, so it was not asked"}
#: keel-cloud 091 FR-F4: the B2C Ability to pay card, derived and never asked.
DERIVED_ABILITY_LINE = "derived from cost and price: already lose your price or more"
#: keel-cloud 091 FR-F1 (`BriefFacts.Card.keelBar`): Keel's bar where Keel sets it, the words after "Keel's bar: ".
KEEL_BAR = {IMPORTANCE_KEY: "holds if at least 2 in 3 put it in their two",
            CURRENT_SOLUTION_KEY: "holds if at least 2 in 3 say today's way falls short (answers 3 to 5)"}
#: What a card's compare reads; `statusWords` is compared on its verdict half (call 82); `keelBar` since 091 (call 114).
CARD_FIELDS = ("key", "name", "number", "line", "status", "keelBar")
PILOT_FIELDS = ("optedIn", "finished", "percent", "perLink")


def lower(text) -> str:
    """A label inside a sentence loses its leading capital -- not an acronym's (keel-cloud 087 call 3)."""
    text = str(text or "").strip()
    return text if len(text) > 1 and text[1].isupper() else text[:1].lower() + text[1:]


def _plain(value) -> str:
    v = float(value)
    return str(int(v)) if v.is_integer() else f"{v:g}"


def _half_up(x) -> int:
    return int(Decimal(repr(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def could_phrase(condition: str) -> str:
    """089 call 4: "They could ..." reads "could ..."; "Could ..." is kept; any other "said yes: {condition}"."""
    text = str(condition or "").strip()
    if text.lower().startswith("they could "):
        return text[len("they "):]
    if text.lower().startswith("could "):
        return lower(text)
    return f"said yes: {lower(text)}"


def _count(standing: dict, name: str = "inside") -> str:
    return f"{standing.get(name)} of {standing.get('n')}"


def _option_count(standing: dict, code: str) -> int:
    for part in str(standing.get("optionCounts") or "").split(","):
        name, _, value = part.strip().partition("=")
        if name == code:
            return int(value)
    return 0


def card(entry, dimension, standing: dict) -> dict:
    """One `BriefFacts.Card` (design §7.2, 089 FR-001): every word code's."""
    key = dimension.key
    status = standing.get("status")
    out = {"key": key, "name": dimension.name}
    if status == "LEFT_OUT":
        out.update(line=LEFT_OUT_LINE)
    elif not standing.get("n"):
        out.update(line=NOBODY_LINE)
    elif key == GATE_KEY:
        out.update(number=f"{standing.get('yes')} of {standing.get('n')}", line=f"had it in {entry.window().words()}")
    elif key == FREQUENCY_KEY:
        unit = ((entry.founder_calibration.get(key) or {}).get("answer") or {}).get("unit")
        out.update(number=f"{_plain(standing.get('median'))} {unit}", line="the middle answer")
    elif key == IMPORTANCE_KEY:
        out.update(number=_count(standing, "own_item_picks"), line="put it in their top two")
    elif key == CURRENT_SOLUTION_KEY:
        out.update(number=_count(standing), line="say today's way falls short")
    elif key == COMPATIBILITY_KEY:
        out.update(number=_count(standing), line=could_phrase((entry.tested(key) or {}).get("label")))
    elif key == "solution.relative_advantage":
        out.update(number=_count(standing), line=f"said it would have made their last {entry.occasion()} better")
    elif key == ADOPTION_KEY:
        out.update(number=_count(standing), line=f"would {lower((entry.tested(key) or {}).get('label'))}")
    elif key == SACRIFICE_KEY:
        cost = entry.cost() or {}
        out.update(number=corpus_mod.money_text(standing.get("median"), cost.get("currency")),
                   line=f"{corpus_mod._PERIOD_WORDS.get(cost.get('period'), '')}, what it costs them today")
    elif key == PRICE_KEY:
        out.update(number=_count(standing), line="at your band or more")
    elif key == ABILITY_KEY:
        out.update(number=_count(standing),
                   line="already lose your price or more" if entry.b2b() else DERIVED_ABILITY_LINE)
    elif key == BUYER_KEY:
        tested = entry.tested(key) or {}
        line = "decided on their own" if tested.get("code") == "nobody_else" \
            else f"{lower(tested.get('label'))} had to agree"
        out.update(number=_count(standing), line=line)
    elif key == PURCHASE_FRICTION_KEY:
        needed = _option_count(standing, "yes_long") + _option_count(standing, "yes_quick")
        out.update(number=f"{needed} of {standing.get('n')}",
                   line=f"needed {lower((entry.tested(key) or {}).get('label'))}")
    elif key == COMMITMENT_KEY:
        out.update(number=_count(standing), line=f"open to {(entry.tested(key) or {}).get('label')}")
    out.update(status=status, statusWords=VERDICT_WORDS.get(status, status))
    if key in KEEL_BAR and status != "LEFT_OUT":
        out["keelBar"] = KEEL_BAR[key]
    return out


def cards_for(entry, registry) -> list:
    """`BriefFacts.cards[]`: one card a calibrated dimension, in registry order (twelve on B2C, thirteen on B2B)."""
    standings = (entry.expected or {}).get("standings") or {}
    return [card(entry, d, standings.get(d.key) or {}) for d in registry.calibrated(entry.b2b())]


def pilot_for(entry) -> dict:
    """`BriefPilot` (089 FR-005): finished = every interview with a response on either link (a gate No too),
    opted in = those who ticked the box; percent whole, half up; per link in the header's words."""
    per = []
    links = [LINK_PRIMARY] + ([LINK_B2B] if entry.b2b() else [])
    for link in links:
        people = [p for p in entry.people() if p.link == link]
        per.append({"link": link, "words": LINK_WORDS[link], "optedIn": sum(1 for p in people if p.pilot_opt_in),
                    "finished": len(people)})
    opted = sum(p["optedIn"] for p in per)
    finished = sum(p["finished"] for p in per)
    return {"optedIn": opted, "finished": finished,
            "percent": _half_up(opted * 100 / finished) if finished else 0, "perLink": per}


def vectors_for(entry) -> list:
    verdicts = (entry.expected or {}).get("vector_verdicts") or {}
    return [{"vector": v, "verdict": (verdicts.get(v) or {}).get("verdict"),
             "words": VERDICT_WORDS.get((verdicts.get(v) or {}).get("verdict"), "Not asked yet")}
            for v in VECTORS]


def decision(entry, registry) -> dict:
    """`BriefFacts.decision` (§4.2 as 082 amended it), over **every** dimension (D3, 089 FR-006)."""
    verdicts = {v["vector"]: v["verdict"] for v in vectors_for(entry)}
    standings = (entry.expected or {}).get("standings") or {}
    problem = [standings.get(d.key) or {} for d in registry.calibrated_slice("PROBLEM", entry.b2b())]
    not_tested = [v for v in VECTORS if verdicts.get(v) == "NOT_TESTED"]
    split = False
    if any(s.get("status") in _THIN for s in problem) or verdicts.get("PROBLEM") == "NOT_TESTED":
        label = "KEEP_INTERVIEWING"
    elif verdicts.get("PROBLEM") != "HOLDING_UP":
        label = "NOT_YET"
        split = verdicts.get("PROBLEM") == "PEOPLE_DISAGREE"
    elif not_tested:
        label = "KEEP_INTERVIEWING"
    elif all(v == "HOLDING_UP" for v in verdicts.values()):
        label = "BUILD"
    else:
        label = "BUILD_BUT_CHANGE"
    counted = [(d.vector, standings[d.key]) for d in registry.calibrated(entry.b2b())
               if (standings.get(d.key) or {}).get("status") not in (None, "NOT_ASKED_YET", "LEFT_OUT")
               and (standings.get(d.key) or {}).get("n") is not None]
    if not counted:
        return {"label": label, "howSure": "LOW", "reason": "Nothing has been asked yet.", "smallestN": 0,
                "split": split, "notTested": not_tested}
    vector, smallest = min(((v, s["n"]) for v, s in counted), key=lambda pair: pair[1])
    too_few = any(s.get("status") == "TOO_FEW_TO_CALL" for _, s in counted)
    disagree = any(s.get("status") == "PEOPLE_DISAGREE" for _, s in counted)
    how = "LOW" if smallest < 5 or too_few else "MEDIUM" if smallest < 10 or disagree else "FAIRLY_SURE"
    who = ("decision-maker" if smallest == 1 else "decision-makers") if entry.b2b() and vector == "COMMERCIAL" \
        else ("person" if smallest == 1 else "people")
    return {"label": label, "howSure": how, "reason": f"Smallest group: {smallest} {who}.", "smallestN": smallest,
            "split": split, "notTested": not_tested}


def broke_of(entry, cards: list, vector: str) -> dict | None:
    """089 FR-002: the one dimension that decided a NOT_HOLDING_UP or PEOPLE_DISAGREE verdict, with its card."""
    verdict = ((entry.expected or {}).get("vector_verdicts") or {}).get(vector) or {}
    if verdict.get("verdict") not in BROKE_ON or not verdict.get("deciding"):
        return None
    found = next((c for c in cards if c["key"] == verdict["deciding"]), None) or {}
    return {k: found.get(k) for k in ("key", "name", "status", "statusWords", "number", "line") if k in found}


def not_asked(entry, registry, vector: str) -> list:
    """089 FR-002's `notAsked`: left out; Ability to pay derived on B2C; Purchase friction on B2C."""
    standings = (entry.expected or {}).get("standings") or {}
    out = []
    for d in registry.slice(vector):
        if d.b2b_only and not entry.b2b():
            out.append({"key": d.key, "name": d.name, "why": NOT_ASKED_WHY[d.key]})
        elif (standings.get(d.key) or {}).get("status") == "LEFT_OUT":
            out.append({"key": d.key, "name": d.name, "why": LEFT_OUT_LINE})
        elif d.b2b_link_only and not entry.b2b():
            out.append({"key": d.key, "name": d.name, "why": NOT_ASKED_WHY[d.key]})
    return out


def targets_for(entry, registry) -> list:
    """The next tests' targets in this reading: the calibrated dimensions that are not holding, worst first, then
    registry order, at most three, each with the items listed and not tested (keel-cloud's own pick also reaches a
    holding one; the BRIEF case is handed keel-cloud's where it has them, call 84)."""
    standings = (entry.expected or {}).get("standings") or {}
    order = {"NOT_HOLDING_UP": 0, "PEOPLE_DISAGREE": 1, "TOO_FEW_TO_CALL": 2, "NOT_ASKED_YET": 3}
    rows = [(order[(standings.get(d.key) or {}).get("status")], i, d) for i, d in
            enumerate(registry.calibrated(entry.b2b())) if (standings.get(d.key) or {}).get("status") in order]
    out = []
    for _rank, _i, d in sorted(rows)[:3]:
        saved = entry.founder_list(d.key) if d.saves.get("picked") else None
        tested = entry.tested(d.key) if saved else None
        not_tested = [i.get("label") for i in (saved or {}).get("items") or []
                      if i is not tested and i.get("code") != "nobody_else"]
        out.append({"key": d.key, "name": d.name, "status": (standings.get(d.key) or {}).get("status"),
                    "n": (standings.get(d.key) or {}).get("n"), "notTested": not_tested})
    return out


def facts_for(entry, registry) -> dict:
    """The reading in `BriefFacts`' shape: header, decision, vectors, money, pilot, cards, the three stages (broke,
    notAsked), targets and keys. No `sharpest` (a cross-tab of two items, keel-cloud's) and no rows."""
    cards = cards_for(entry, registry)
    cost = entry.cost() or {}
    price = entry.price() or {}
    currency = cost.get("currency") or price.get("currency") or \
        corpus_mod.MARKET_CURRENCY.get((entry.market or {}).get("country"))
    period = cost.get("period") or price.get("period")
    people = [{"link": link, "words": LINK_WORDS[link], "people": sum(1 for p in entry.people() if p.link == link)}
              for link in ([LINK_PRIMARY] + ([LINK_B2B] if entry.b2b() else []))]
    out = {
        "header": {"project": entry.title, "segment": (entry.context or {}).get("segment"), "people": people},
        "decision": decision(entry, registry),
        "vectors": vectors_for(entry),
        "money": {"currency": currency, "currencySymbol": CURRENCY_SYMBOL.get(currency, f"{currency} "
                                                                          if currency else None),
                  "period": period, "periodWords": corpus_mod._PERIOD_WORDS.get(period) if period else None},
        "pilot": pilot_for(entry),
        "cards": cards,
    }
    for vector in VECTORS:
        stage = {"notAsked": not_asked(entry, registry, vector)}
        broke = broke_of(entry, cards, vector)
        if broke:
            stage = {"broke": broke, **stage}
        out[vector.lower()] = stage
    out["targets"] = targets_for(entry, registry)
    out["keys"] = registry.calibrated_keys(entry.b2b())
    return out


def beliefs_for(entry, registry) -> list:
    """`beliefs`: per calibrated dimension `{key, name, belief_sentence, founder_phrase}` (no weight since 087) --
    the phrase the corpus records, else the list's own phrase (Current solution's), else the tested item's label."""
    out = []
    for d in registry.calibrated(entry.b2b()):
        calibration = entry.founder_calibration.get(d.key) or {}
        phrase = calibration.get("belief_phrase")
        if phrase is None and d.founder_list and not calibration.get("unsure"):
            saved = entry.founder_list(d.key) or {}
            phrase = saved.get("phrase") or (entry.tested(d.key) or {}).get("label")
        out.append({"key": d.key, "name": d.name, "belief_sentence": calibration.get("belief_sentence"),
                    "founder_phrase": phrase})
    return out


def stories_for(entry) -> list:
    """`stories`: each readable person's story by invitation id (the person's id, here)."""
    return [{"invitation_id": f"{entry.id}/{p.person}", "link": p.link, "story": p.story}
            for p in entry.people() if p.readable]


# ----------------------------------------------------------------------------------- the compare

class FactsCompare:
    """One entry's DRY compare: the marked checks (cards, the pilot) and the reported differences."""

    def __init__(self, entry_id: str):
        self.entry_id = entry_id
        self.checks = 0
        self.agreed = 0
        self.mismatches = []
        self.reported_diffs = []
        self.measured = True
        self.reason = None

    @property
    def correctness(self):
        return (self.agreed / self.checks) if (self.measured and self.checks) else None


def _head(words) -> str:
    return str(words or "").split(" · ", 1)[0]


def compare(entry, registry, cloud_facts: dict | None) -> FactsCompare:
    """keel-cloud's facts for one entry against this reading: one marked check a card and one the pilot."""
    score = FactsCompare(entry.id)
    if not isinstance(cloud_facts, dict):
        score.measured = False
        score.reason = f"keel-cloud wrote no brief facts for {entry.id}"
        return score
    mine = cards_for(entry, registry)
    theirs = {c.get("key"): c for c in cloud_facts.get("cards") or []}
    for card_ in mine:
        got = theirs.get(card_["key"]) or {}
        score.checks += 1
        want = {k: card_.get(k) for k in CARD_FIELDS} | {"statusWords": _head(card_.get("statusWords"))}
        have = {k: got.get(k) for k in CARD_FIELDS} | {"statusWords": _head(got.get("statusWords"))}
        if want == have:
            score.agreed += 1
        else:
            score.mismatches.append({"key": card_["key"], "expected": want, "produced": have})
        if " · " in str(got.get("statusWords") or ""):
            score.reported_diffs.append({"key": card_["key"], "field": "statusWords (insight)",
                                         "expected": None, "produced": got["statusWords"].split(" · ", 1)[1]})
    for key in sorted(set(theirs) - {c["key"] for c in mine}):
        score.checks += 1
        score.mismatches.append({"key": key, "expected": None, "produced": theirs[key]})
    pilot = pilot_for(entry)
    got = {k: (cloud_facts.get("pilot") or {}).get(k) for k in PILOT_FIELDS}
    score.checks += 1
    if pilot == got:
        score.agreed += 1
    else:
        score.mismatches.append({"key": "pilot", "expected": pilot, "produced": got})
    for name, want, have in (
            ("decision", decision(entry, registry), cloud_facts.get("decision")),
            ("vectors", vectors_for(entry), cloud_facts.get("vectors"))):
        if want != have:
            score.reported_diffs.append({"key": name, "field": name, "expected": want, "produced": have})
    for vector in VECTORS:
        stage = cloud_facts.get(vector.lower()) or {}
        want = (broke_of(entry, mine, vector) or {}).get("key")
        have = (stage.get("broke") or {}).get("key")
        if want != have:
            score.reported_diffs.append({"key": vector, "field": "broke", "expected": want, "produced": have})
        want_na = [n["key"] for n in not_asked(entry, registry, vector)]
        have_na = [n.get("key") for n in stage.get("notAsked") or []]
        if want_na != have_na:
            score.reported_diffs.append({"key": vector, "field": "notAsked", "expected": want_na,
                                         "produced": have_na})
    return score


def unmeasured(entry_id: str, reason: str) -> FactsCompare:
    score = FactsCompare(entry_id)
    score.measured = False
    score.reason = reason
    return score
