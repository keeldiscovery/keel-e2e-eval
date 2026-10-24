"""The eval's own reading of a corpus entry's `BriefFacts` -- the cards, the pilot, the decision, what broke -- and
its DRY compare against keel-cloud's (spec 040 FR-006; keel-cloud 089 FR-001, FR-002, FR-005, FR-006; judgement
calls 82-84).

keel-cloud assembles `BriefFacts` from a project's stored answers by `StandingsAssembler` and `BriefFacts.of`, and its
`BriefFactsCorpusTest` writes each corpus entry's whole facts (`build/brief-facts/<entry>.json`,
`instructions/cloud_corpus.py`). This module reads the same entry the other way round -- from its
`expected.standings`, `expected.vector_verdicts`, the founder's lists and each answer's `pilot_opt_in`, by the words
design §7.2 and keel-cloud 089 state -- and `compare` holds keel-cloud's to it:

- **marked** (`brief_facts`, one check a card, one the pilot and one the price median): every card's `key`, `name`,
  `number`, `line`, `status`, `keelBar` (keel-cloud 091 FR-F1: Keel's bar on Importance and Current solution, absent
  elsewhere and on a left-out card; spec 042 call 114) and the verdict half of its `statusWords`; the pilot's
  `optedIn`, `finished`, `percent` and `perLink`; and (spec 052, keel-cloud 104 FR-1, design §3 D11) the price
  median's `edgeSaid`, `chose` and `n`, or its absence;
- **reported, never marked** (call 3): the insight half of `statusWords` (spec 082's words, keel-cloud's own), the
  decision, the vector words, each stage's `broke` key and `notAsked` keys.

The arithmetic here is the corpus's own counts restated, never the engine's: `n`, `inside`, `own_item_picks`,
`optionCounts`, `median` and `yes` are read off the standings the checker and `GoldenCorpusTest` pin; nothing is
recounted from the picks but the pilot, which no standing carries. The price table is Price's own `optionCounts`
restated over the founder's ladder (`price_table`).

`facts_for` is the same reading in `BriefFacts`' shape (without `sharpest`, `targets` and `keys`, which keel-cloud 104
deleted), what `instructions/overview.py` draws the corpus's Overview from (spec 052, `report_overview`).
"""

from __future__ import annotations

import re
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
            CURRENT_SOLUTION_KEY: "holds if at least 2 in 3 say today's way falls short (answers 3 to 5)",
            # spec 064 FR-7 (keel-cloud 118 FR-3): the fear's bar
            PURCHASE_FRICTION_KEY: "holds if at least 2 in 3 say it was needed last time and took a long time"}


def current_solution_bar(rung: str) -> str:
    """Spec 064 FR-5a (keel-cloud 117 FR-3, `BriefFacts.currentSolutionBar`): Current solution's bar names the
    founder's worst acceptable rung -- the outcome just above the list's line (D4's 2 where the list carries none)."""
    return f"holds if at least 2 in 3 land below '{rung.strip()}'"


def prevalence_line(clause: str | None, window_words: str) -> str:
    """Spec 064 FR-4a (keel-cloud 116 FR-3, `BriefFacts.prevalenceLine`): the founder's own clause in the window --
    *had to recount stock by hand after a mismatched delivery in the last 4 weeks* -- the clause's own past verb is the
    line's *had*; *had it in {window}* where no clause can be read (a corpus entry records none)."""
    text = " ".join(str(clause or "").split())
    while text.endswith("."):
        text = text[:-1].strip()
    if len(text) > 1 and text[0].isupper() and not text[1].isupper():
        text = text[0].lower() + text[1:]
    return f"{text} in {window_words}" if text else f"had it in {window_words}"


def frequency_line(clause: str | None, window) -> str:
    """keel-cloud 130 FR-2 (`BriefFacts.frequencyLine`): *the middle answer · {the window's unit, plural} they {the served
    gate's clause}* -- *months they had rupees left over ...* on a month window, *days* only on a day window; *the
    middle answer* where no gate is stored (a corpus entry). `window` is a `registry.RecallWindow`."""
    return "the middle answer" if clause is None else f"the middle answer · {window.plural} they {clause}"


def gate_clause_of_them(gate_question: str | None, window) -> str | None:
    """keel-cloud 130 FR-6 (`BriefFacts.servedGateClause`'s new branch): a served gate whose clause names its own subject
    (*In the last 7 days, did a booking call come in on your shift?*) is said of the people as what they had happen --
    *had a booking call come in on their shift* -- the Prevalence and Frequency lines' clause. Read off the gate's own
    frame (`WindowFrame.eventFromGate`): code frames *did you {clause}* or *did your ...* for a clause of the person's,
    *did {clause}* only for one with a subject of its own, so the frame tells the two apart. None for the person's own
    clause (code says it in its own past tense, `StrangerGrammar.saidOfThem`, not mirrored here) or a gate not in code's
    frame."""
    prefix = f"In {window.words()}, did "
    text = str(gate_question or "").strip()
    if not text.startswith(prefix) or not text.endswith("?"):
        return None
    event = text[len(prefix):-1].strip()
    low = event.lower()
    if not event or low == "you" or low.startswith(("you ", "your ")):
        return None
    return "had " + re.sub(r"\byour\b", "their", re.sub(r"\byours\b", "theirs",
                                                          re.sub(r"\byourself\b", "themselves", event)))


#: keel-cloud 122 FR-3 (`facts.decision.change`, `DecisionChangeCorpusTest`): the seven golden decisions' named change,
#: copied from keel-cloud's `specs/122-.../tasks.md` table (*After*); `instructions/overview.py` draws it in place of the
#: semicolon list it used to join (spec 064 FR-8c). Read on the corpus reading only; a journey reads the served change.
#: Spec 067 (keel-cloud 128 FR-8, `ChangeSentences.namedAgainst`): each count names the side against the founder --
#: *only k of n ..., and n - k did not* -- copied from keel-cloud's `build/brief-facts/` at keel-cloud-docs `423f0983`.
DECISION_CHANGE = {
    "01-countly": {"line": CURRENT_SOLUTION_KEY,
                   "sentence": "Not yet: Current solution split them, only 5 of 8 say today's way falls short, and 3 did not."},
    "02-compliancelog": {"line": "solution.relative_advantage",
                         "sentence": "Build, but change what it does better: only 4 of 9 said it would have made their "
                                     "last compliance report better, and 5 did not.",
                         "also": {"line": PRICE_KEY,
                                  "sentence": "Change the price too: 7 of 9 put it below your $250 to $350 a month."}},
    "03-lullaby": {"line": CURRENT_SOLUTION_KEY,
                   "sentence": "Not yet: Current solution did not hold, only 2 of 8 say today's way falls short, and 6 did "
                               "not.",
                   "also": {"line": IMPORTANCE_KEY,
                            "sentence": "Importance split them too, only 3 of 8 put it in their top two, and 5 did not."}},
    "04-linerly": {"line": IMPORTANCE_KEY, "sentence": "Not yet: Importance split them, only 3 of 8 put it in their top two, and 5 "
                                                            "did not.",
                   "also": {"line": CURRENT_SOLUTION_KEY,
                            "sentence": "Current solution split them too, only 3 of 8 say today's way falls short, and 5 did "
                                        "not."}},
    "05-paidly": {"line": SACRIFICE_KEY,
                  "sentence": "Build, but change the cost you put on the problem: the middle cost was $58.33 a month "
                              "against your $100 to $300 a month.",
                  "also": {"line": PRICE_KEY,
                           "sentence": "Change the price too: 3 of 8 put it below your $60 to $100 a month."}},
    "06-repeatline": {"line": "solution.relative_advantage",
                      "sentence": "Build, but change what it does better: only 3 of 9 said it would have made their "
                                  "last shift on the phones better, and 6 did not.",
                      "also": {"line": COMMITMENT_KEY,
                               "sentence": "Change the first step you ask for too: only 2 of 7 would introduce us to the "
                                           "practice's IT supplier, and 5 did not."}},
    "07-mulchrun": {"line": GATE_KEY,
                    "sentence": "Not yet: Prevalence did not hold, 9 of 12 had it in the last 2 weeks against your "
                                "nearly all.",
                    "also": {"line": IMPORTANCE_KEY,
                             "sentence": "Importance split them too, only 4 of 7 put it in their top two, and 3 did not."}},
}
#: What a card's compare reads; `statusWords` is compared on its verdict half (call 82); `keelBar` since 091 (call 114).
CARD_FIELDS = ("key", "name", "number", "line", "status", "keelBar")
PILOT_FIELDS = ("optedIn", "finished", "percent", "perLink")
#: keel-cloud 104 `BriefFacts.PriceMedian`: what the price tile says (`edge` is its number, not compared).
PRICE_MEDIAN_FIELDS = ("edgeSaid", "chose", "n")


def lower(text) -> str:
    """A label inside a sentence loses its leading capital -- not an acronym's (keel-cloud 087 call 3)."""
    text = str(text or "").strip()
    return text if len(text) > 1 and text[1].isupper() else text[:1].lower() + text[1:]


def _plain(value) -> str:
    v = float(value)
    return str(int(v)) if v.is_integer() else f"{v:g}"


def _half_up(x) -> int:
    return int(Decimal(repr(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


#: keel-cloud 103 `BriefFacts.couldPhrase`: the line when the tested condition carries no words.
COULD_PHRASE_BLANK = "said yes, easily or with some steps"


def could_phrase(condition: str) -> str:
    """keel-cloud 103 FR-9 (design §3, fixing 089 call 4): "They could ..." reads "could ..."; "Could ..." is kept;
    any other subject is kept after "said" ("The agency could ..." -> "said the agency could ..."); no "said yes:"."""
    text = str(condition or "").strip()
    if not text:
        return COULD_PHRASE_BLANK
    lowered = lower(text)
    if lowered.lower().startswith("they could "):
        return lowered[len("they "):]
    if lowered.lower().startswith("could "):
        return lowered
    return f"said {lowered}"


def _count(standing: dict, name: str = "inside") -> str:
    return f"{standing.get(name)} of {standing.get('n')}"


def _option_count(standing: dict, code: str) -> int:
    # the wire's `DimensionStanding.choice.optionCounts` (`[{code, count}]`, keel-web 106's `barWords` reads it), else
    # the corpus's `optionCounts` string
    served = ((standing.get("choice") or {}) if isinstance(standing.get("choice"), dict) else {}).get("optionCounts")
    if isinstance(served, list):
        return int(next((o.get("count") or 0 for o in served if isinstance(o, dict) and o.get("code") == code), 0))
    for part in str(standing.get("optionCounts") or "").split(","):
        name, _, value = part.strip().partition("=")
        if name == code:
            return int(value)
    return 0


def _split(supports: int, n: int) -> str:
    """keel-cloud `Compare.split`: at least 2 in 3 holds, at most 1 in 3 does not, else a split (n under 5 too few)."""
    if n < 5:
        return "TOO_FEW_TO_CALL"
    if supports * 3 >= 2 * n:
        return "HOLDING_UP"
    if supports * 3 <= n:
        return "NOT_HOLDING_UP"
    return "PEOPLE_DISAGREE"


#: keel-cloud 128 FR-8 (`BriefFacts.BAR_LINES`): the lines the founder sets a bar on, where the bar decides first.
BAR_LINES = (COMPATIBILITY_KEY, "solution.relative_advantage", ADOPTION_KEY, PURCHASE_FRICTION_KEY, COMMITMENT_KEY)
#: keel-cloud 128 FR-8 (`BriefFacts.DID_NOT_HOLD`): a bar line past its bar.
DID_NOT_HOLD = "Did not hold"


def bar_words(key: str, standing: dict) -> str:
    """keel-cloud 128 FR-8 (`BriefFacts.barWords`, spec 067): a status's words -- on a line with a founder's bar the
    engine's amber is never said *People disagree*: past the bar it *Did not hold*, and Purchase friction's fear that held
    (`yes_long` at two in three or more) is *Holding up*. The status and every count are the engine's, unchanged."""
    status = standing.get("status")
    if status != "PEOPLE_DISAGREE" or key not in BAR_LINES:
        return VERDICT_WORDS.get(status, status)
    if key == PURCHASE_FRICTION_KEY and standing.get("n") \
            and _split(_option_count(standing, "yes_long"), int(standing["n"])) == "HOLDING_UP":
        return VERDICT_WORDS["HOLDING_UP"]
    return DID_NOT_HOLD


def friction_words(key: str, standing: dict, tested: str | None, words: str) -> str:
    """Spec 064 FR-7 (keel-cloud 118 FR-3, `BriefFacts.frictionWords`): a friction line's words -- Purchase friction (a
    fear) held *Yes, {step} slows it. Plan for it.*, not held *Your fear was {step}. k of n said it was quick or not
    needed. Not the blocker you expected.*; Adoption friction (an effort) not held *{Effort} is too much for k of n*;
    a split and anything else keep the status words."""
    status = standing.get("status")
    n = int(standing.get("n") or 0)
    if status not in ("HOLDING_UP", "NOT_HOLDING_UP", "PEOPLE_DISAGREE") or not tested or not n:
        return words
    step = lower(tested.strip())
    if key == PURCHASE_FRICTION_KEY:
        held = _option_count(standing, "yes_long")
        belief = _split(held, n)
        if belief == "HOLDING_UP":
            return f"Yes, {step} slows it. Plan for it."
        if belief == "NOT_HOLDING_UP":
            return (f"Your fear was {step}. {n - held} of {n} said it was quick or not needed. Not the blocker you "
                    "expected.")
        return words
    against = _option_count(standing, "probably_not") + _option_count(standing, "no")
    if _split(n - against, n) == "NOT_HOLDING_UP":
        return f"{step[:1].upper() + step[1:]} is too much for {against} of {n}"
    return words


def card(entry, dimension, standing: dict, *, clause: str | None = None) -> dict:
    """One `BriefFacts.Card` (design §7.2, 089 FR-001): every word code's. `clause` (spec 064 FR-4a): the founder's
    Prevalence clause the study carries (a journey's scripted one), else none -- a corpus entry records none."""
    key = dimension.key
    status = standing.get("status")
    out = {"key": key, "name": dimension.name}
    if status == "LEFT_OUT":
        out.update(line=LEFT_OUT_LINE)
    elif not standing.get("n"):
        out.update(line=NOBODY_LINE)
    elif key == GATE_KEY:
        out.update(number=f"{standing.get('yes')} of {standing.get('n')}",
                   line=prevalence_line(clause, entry.window().words()))
    elif key == FREQUENCY_KEY:
        unit = ((entry.founder_calibration.get(key) or {}).get("answer") or {}).get("unit")
        # keel-cloud 129 FR-1 (`BriefFacts.card`, T003): where the study stores a gate (a journey's scripted one), the
        # units counted are the served gate's -- the corpus's line alone otherwise; keel-cloud 130 FR-2
        # (`BriefFacts.frequencyLine`): in the window's unit, 05-paidly's *months they waited ...*, never *days*
        out.update(number=f"{_plain(standing.get('median'))} {unit}", line=frequency_line(clause, entry.window()))
    elif key == IMPORTANCE_KEY:
        out.update(number=_count(standing, "own_item_picks"), line="put it in their top two")
    elif key == CURRENT_SOLUTION_KEY:
        out.update(number=_count(standing), line="say today's way falls short")
    elif key == COMPATIBILITY_KEY:
        out.update(number=_count(standing), line=could_phrase((entry.tested(key) or {}).get("label")))
    elif key == "solution.relative_advantage":
        out.update(number=_count(standing), line=f"said it would have made their last {entry.occasion()} better")
    elif key == ADOPTION_KEY:
        # keel-cloud 118 FR-2: the effort as asked -- the plain yes; "if it was clearly worth it" apart, after it
        apart = _option_count(standing, "yes_if_worth_it")
        out.update(number=f"{_option_count(standing, 'yes')} of {standing.get('n')}",
                   line=f"would {lower((entry.tested(key) or {}).get('label'))}"
                        + (f" · {apart} more if it was clearly worth it" if apart else ""))
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
        # keel-cloud 118 FR-3: the fear's supporters -- needed, and it took a long time
        step = (entry.tested(key) or {}).get("label")
        out.update(number=f"{_option_count(standing, 'yes_long')} of {standing.get('n')}",
                   line=f"needed {lower(step) if step else 'the step'}, and it took a long time")
    elif key == COMMITMENT_KEY:
        # keel-cloud 118 FR-2: the step as asked is the number; the second yes beside it, apart
        apart = _option_count(standing, "yes_after_trying")
        smaller = (entry.founder_list(key) or {}).get("items") or []
        second = lower(smaller[1]["label"]) if len(smaller) > 1 else None
        out.update(number=f"{_option_count(standing, 'yes_start')} of {standing.get('n')}",
                   line=f"would {(entry.tested(key) or {}).get('label') or 'take the step'}"
                        + (f" · {apart} more {'after ' + second + ' first' if second else 'after trying it first'}"
                           if apart else ""))
    out.update(status=status, statusWords=bar_words(key, standing))
    if key in (ADOPTION_KEY, PURCHASE_FRICTION_KEY) and standing.get("n"):
        out["statusWords"] = friction_words(key, standing, (entry.tested(key) or {}).get("label"), out["statusWords"])
    if key in KEEL_BAR and status != "LEFT_OUT":
        out["keelBar"] = KEEL_BAR[key]
        if key == CURRENT_SOLUTION_KEY:
            saved = entry.founder_list(key) or {}
            items = saved.get("items") or []
            if len(items) >= 2:
                out["keelBar"] = current_solution_bar(items[1]["label"])
    return out


def cards_for(entry, registry) -> list:
    """`BriefFacts.cards[]`: one card a calibrated dimension, in registry order (twelve on B2C, thirteen on B2B)."""
    standings = (entry.expected or {}).get("standings") or {}
    return [card(entry, d, standings.get(d.key) or {}) for d in registry.calibrated(entry.b2b())]


def not_counted(gate_no: int, outside: int) -> str | None:
    """keel-cloud 123 FR-4 (`BriefFacts.notCounted`): the pilot tile's small line, or None when nobody is left out."""
    parts = ([f"{gate_no} who did not have it"] if gate_no else []) + (
        [f"{outside} outside who the study is for"] if outside else [])
    return f"Not counted: {' and '.join(parts)}." if parts else None


def pilot_for(entry) -> dict:
    """`BriefPilot` (089 FR-005): opted in = those who ticked the box; percent whole, half up; per link in the header's
    words. Spec 064 FR-6a (keel-cloud 123 FR-4): on the primary link `finished` counts the people who have it -- a gate
    Yes -- alone; a gate No and a person outside the segment are named in `notCounted` and counted nowhere else (the
    decision-maker's link unchanged)."""
    per = []
    links = [LINK_PRIMARY] + ([LINK_B2B] if entry.b2b() else [])
    for link in links:
        people = [p for p in entry.people() if p.link == link]
        row = {"link": link, "words": LINK_WORDS[link]}
        if link == LINK_PRIMARY:
            has_it = [p for p in people if p.gate_yes]
            gate_no = sum(1 for p in people if p.in_segment and p.recency != "yes")
            outside = sum(1 for p in people if not p.in_segment)
            row.update(optedIn=sum(1 for p in has_it if p.pilot_opt_in), finished=len(has_it))
            line = not_counted(gate_no, outside)
            if line:
                row["notCounted"] = line
        else:
            row.update(optedIn=sum(1 for p in people if p.pilot_opt_in), finished=len(people))
        per.append(row)
    opted = sum(p["optedIn"] for p in per)
    finished = sum(p["finished"] for p in per)
    return {"optedIn": opted, "finished": finished,
            "percent": _half_up(opted * 100 / finished) if finished else 0, "perLink": per}


def _floor_of(code: str):
    """`PriceLadder.floorOf`: *under* reads 0, a band or *over* its low edge, anything else (`would_not_pay`) none."""
    parts = str(code or "").split("_")
    if parts[0] == "under":
        return 0
    if parts[0] in ("band", "over") and len(parts) > 1:
        return float(parts[1])
    return None


def _edges(low) -> list:
    """`PriceLadder.bands(low)`' low edges, the Under band having none: three bands' lows and the Over band's."""
    return [_floor_of(code) for code in corpus_mod.price_ladder_codes(low)
            if code.startswith(("band_", "over_"))]


def _money_of(entry) -> tuple:
    cost = entry.cost() or {}
    price = entry.price() or {}
    currency = cost.get("currency") or price.get("currency") or \
        corpus_mod.MARKET_CURRENCY.get((entry.market or {}).get("country"))
    period = cost.get("period") or price.get("period")
    return currency, period


def edge_said(edge, currency, period) -> str:
    """`BriefFacts.said`: the amount in the market's money, then the period's words (*$50 a month*)."""
    words = corpus_mod._PERIOD_WORDS.get(period) if period else None
    return corpus_mod.money_text(edge, currency) + (f" {words}" if words else "")


def price_table(founder_low, bands: list, *, currency=None, period=None) -> list | None:
    """`BriefFacts.priceTable`'s `chose` column (§4.5): one row per low edge of the founder's ladder, each the number
    of the counted Price picks (`bands`, the codes) whose band starts at or above it. `None` off the ladder."""
    if not corpus_mod.price_placeable(founder_low):
        return None
    floors = [_floor_of(b) for b in bands]
    return [{"edge": edge, "edgeSaid": edge_said(edge, currency, period),
             "chose": sum(1 for f in floors if f is not None and f >= edge)}
            for edge in _edges(founder_low)]


def price_median(rows: list | None, n: int) -> dict | None:
    """keel-cloud 104 FR-1 (design §3, D11): the **highest** row at least half of `n` chose at or above
    (`chose * 2 >= n`, so an exact half qualifies) -- `{edgeSaid, chose, n}`; `None` with no table, `n == 0` or no
    row that reaches half. A floor, never a point: the answers are bands."""
    if not rows or not n:
        return None
    best = None
    for row in rows:
        if row["chose"] * 2 >= n and (best is None or row["edge"] > best["edge"]):
            best = row
    return None if best is None else {"edgeSaid": best["edgeSaid"], "chose": best["chose"], "n": n}


def price_median_for(entry) -> dict | None:
    """The entry's price median: its Price standing's `optionCounts` (the counted picks: anchored, a band or *would
    not pay*, never an escape) over the founder's ladder. `None` where Price was left out, the founder gave no price,
    or nobody counted answered it."""
    standing = ((entry.expected or {}).get("standings") or {}).get(PRICE_KEY) or {}
    price = entry.price() or {}
    if standing.get("status") == "LEFT_OUT" or not price or price.get("unsure") or not standing.get("n"):
        return None
    bands = [code for code, count in _option_counts_all(standing).items() for _ in range(count)]
    currency, period = _money_of(entry)
    return price_median(price_table(price.get("low"), bands, currency=currency, period=period), len(bands))


def _option_counts_all(standing: dict) -> dict:
    out = {}
    for part in str(standing.get("optionCounts") or "").split(","):
        name, _, value = part.strip().partition("=")
        if name:
            out[name] = int(value or 0)
    return out


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
    out = {"label": label, "howSure": how, "reason": f"Smallest group: {smallest} {who}.", "smallestN": smallest,
           "split": split, "notTested": not_tested}
    if label in ("BUILD_BUT_CHANGE", "NOT_YET") and entry.id in DECISION_CHANGE:
        out["change"] = DECISION_CHANGE[entry.id]
    return out


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


def facts_for(entry, registry) -> dict:
    """The reading in `BriefFacts`' shape: header, decision, vectors, money, pilot, cards, the three stages (broke,
    notAsked; `commercial.priceMedian`, keel-cloud 104). No `sharpest`, `targets` or `keys` (keel-cloud 104 deleted
    them) and no rows."""
    cards = cards_for(entry, registry)
    currency, period = _money_of(entry)
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
        if vector == "COMMERCIAL":
            stage["priceMedian"] = price_median_for(entry)
        out[vector.lower()] = stage
    return out


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
    """keel-cloud's facts for one entry against this reading: one marked check a card, one the pilot and one the price
    median (`facts.commercial.priceMedian`, `{edgeSaid, chose, n}` or null; keel-cloud 104)."""
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
    want_median = price_median_for(entry)
    commercial = cloud_facts.get("commercial") or {}
    have = commercial.get("priceMedian")
    have_median = {k: have.get(k) for k in PRICE_MEDIAN_FIELDS} if isinstance(have, dict) else None
    score.checks += 1
    if have_median == want_median:
        score.agreed += 1
    else:
        score.mismatches.append({"key": "priceMedian", "expected": want_median, "produced": have})
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
