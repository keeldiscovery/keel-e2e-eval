"""The commercial chain's words, ladder and reading (spec 064 FR-1; keel-cloud 115 / 124), read-only ports.

keel-cloud 115 put the commercial chain on the wire -- a founder's cost today in three modes (MONEY, HOURS, RATE, over
one of six periods, `each` among them, per the founder's own unit), a price in four shapes (an amount a period, a share,
up front then a plan, free to them) that takes the cost's unit and period, and an Ability to pay that is a *reading* of
the two, never a ratio derived from money that does not compare. Corpus revision 13 (keel-cloud 124) lets an entry state
it, and its checker's rule C holds every word of it to the engine.

Nothing here is the eval's own arithmetic: every function is a port of keel-cloud's `CommercialChain` as
`canon/designs/measured-beliefs/sim/check_corpus_r13.py` ports it (the "as built" FR-1a names), so the loader's
refusals say what the checker says and the harness's read-backs (the equation line, the locked words) are the
engine's. A cost with no `unit` (and of mode AMOUNT or HOURS) and a price with no `shape` are *not* the chain's -- they
are read exactly as revision 12 reads them (`cost_in_chain`, `price_in_chain`).

Judgement call (064): keel-cloud 122 T017 ran the money ladder on to 100,000,000; the r13 checker's points stop at a
million and its refusal says "under 1,000,000". This module follows the checker (FR-1a), which serves the same codes for
every founder's low under 250,000 -- every entry's.
"""

from __future__ import annotations

import math
import re
from decimal import ROUND_HALF_UP
from decimal import Decimal as D

#: keel-cloud `Period.wires()` since 115: the five periods and `each` (no length, never normalised).
CHAIN_PERIODS = ("day", "week", "month", "quarter", "year", "each")
CHAIN_PERIOD_WORDS = {"day": "a day", "week": "a week", "month": "a month", "quarter": "a quarter",
                      "year": "a year", "each": "each"}
#: `CalibrationAnswer.Cost` modes: the chain's three, and AMOUNT still taken (read as money).
CHAIN_COST_MODES = ("MONEY", "HOURS", "RATE", "AMOUNT")
CHAIN_MODES = ("MONEY", "HOURS", "RATE")
PRICE_SHAPES = ("AMOUNT_PERIOD", "SHARE", "UPFRONT_THEN", "FREE")
SHARE_BASES = ("COST_BASE", "RECOVERED")
MONEY_POINTS = tuple(D(x) for x in (
    "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2", "5", "10", "20", "50", "100", "250", "500", "1000", "2500",
    "5000", "10000", "25000", "50000", "100000", "250000", "500000", "1000000"))
PERCENT_POINTS = tuple(D(x) for x in ("0.01", "0.02", "0.05", "0.1", "0.25", "0.5", "1", "2", "5", "10", "25", "50",
                                      "100"))
UPFRONT = "upfront."
WOULD_NOT_PAY = "would_not_pay"
#: `CommercialChain.CONSUMER_BUDGET` (keel-cloud 124 FR-1a: the engine's, not the spec's first spelling), escape cant_say.
CONSUMER_BUDGET = ("from_spend", "new_money", "could_not")
CONSUMER_BUDGET_ESCAPE = "cant_say"
#: What supports on a budget reading: money already there (keel-cloud 115 judgement call 12).
BUDGET_SUPPORTS = ("from_spend", "existing_line", "taken_from_other_spend")
READINGS = ("compare", "out_of_gain", "from_what_comes_back", "free", "budget")
CHAIN_FIELDS_COST = frozenset({"mode", "low", "high", "rate", "period", "currency", "measure", "base", "unit",
                               "lossPhrase"})
CHAIN_FIELDS_PRICE = frozenset({"shape", "low", "high", "upfrontLow", "upfrontHigh", "thenNothing", "shareBase",
                                "currency"})
#: The value box's row (keel-cloud 115 FR-2): the registry's one escape, and the chips code adds.
VALUE_BOX_CONTROL = "value_box"
VALUE_BOX_ESCAPE = "dont_know"
VALUE_BOX_CHIPS = ("dont_know", "rather_not_say")
#: A price's amount bounds (the r13 checker's): a share 0.01 to under 100, an amount 0.01 to under 1,000,000.
SHARE_TOP = 100
AMOUNT_TOP = 1_000_000
_SYMBOL = {"GBP": "£", "USD": "$", "EUR": "€"}


def dec(x):
    return None if x is None else D(str(x))


def plain(d) -> str:
    """BigDecimal.stripTrailingZeros().toPlainString()."""
    return format(D(d).normalize(), "f")


def grouped(d) -> str:
    s = D(d).normalize()
    return f"{int(s):,}" if s == s.to_integral_value() else f"{s:,.2f}"


def cnumber(d) -> str:
    """CommercialChain.number: the founder's number as typed, thousands grouped."""
    s = D(d).normalize()
    if s == s.to_integral_value():
        return f"{int(s):,}"
    p = format(s, "f")
    return f"{int(s):,}" + p[p.index("."):]


def cmoney(d, currency) -> str:
    """CostEstimate.amount: the symbol, then PriceLadder.money of the value rounded to cents."""
    d = D(d)
    s = d.normalize()
    rounded = s if s == s.to_integral_value() else d.quantize(D("0.01"), ROUND_HALF_UP)
    return _SYMBOL.get(currency, (currency or "") + " ") + grouped(rounded)


def _range(low, high, lo, hi) -> str:
    return low if lo == hi else f"{low} to {high}"


def the(role: str) -> str:
    """"the {decider}" unless the role already carries an article, a possessive or a capital."""
    r = role.lower()
    if r.startswith(("the ", "a ", "an ", "their ", "your ", "my ")):
        return role
    if len(role) > 1 and role[0].isupper() and not role[1].isupper():
        return role
    return "the " + role


def is_money(cost: dict) -> bool:
    return cost.get("mode") in ("MONEY", "AMOUNT")


def measure_of(cost: dict):
    m = cost.get("measure")
    if isinstance(m, str) and m.strip():
        return m.strip()
    return "hours" if cost.get("mode") == "HOURS" else "$" if is_money(cost) else None


def is_percent(cost: dict) -> bool:
    return cost.get("mode") == "RATE" and measure_of(cost) == "%"


def cost_in_chain(cost) -> bool:
    """CalibrationAnswer.Cost.chain: a unit, or a mode only the chain has."""
    return isinstance(cost, dict) and (cost.get("unit") is not None or cost.get("mode") in ("MONEY", "RATE"))


def price_in_chain(price) -> bool:
    return isinstance(price, dict) and price.get("shape") is not None


def figure(cost: dict, lo, hi) -> str:
    if is_money(cost):
        return _range(cmoney(lo, cost.get("currency")), cmoney(hi, cost.get("currency")), lo, hi)
    m = measure_of(cost)
    if m == "%":
        return _range(cnumber(lo) + "%", cnumber(hi) + "%", lo, hi)
    return _range(cnumber(lo), cnumber(hi), lo, hi) + ("" if m is None else " " + m)


def per(unit, period) -> str:
    words = CHAIN_PERIOD_WORDS.get(period, "")
    if not unit or not str(unit).strip():
        return words
    return "per " + unit.strip() + ("" if not words else (", " if period == "each" else " ") + words)


def base_of(cost, occasion):
    b = cost.get("base") if cost else None
    return b.strip() if isinstance(b, str) and b.strip() else (occasion.strip() if occasion else None)


def unit_of(cost, role_word):
    u = cost.get("unit") if cost else None
    return u.strip() if isinstance(u, str) and u.strip() else (role_word.strip() if role_word else None)


def cost_said(cost: dict, occasion, role_word) -> str:
    """CommercialChain.costSaid: the phrase the drift clause quotes (the belief phrase)."""
    unit, lo, hi = unit_of(cost, role_word), dec(cost["low"]), dec(cost["high"])
    if cost["mode"] == "RATE":
        of = base_of(cost, occasion)
        return "about " + figure(cost, lo, hi) + ("" if of is None else " of " + of) + " " + per(unit, cost["period"])
    return ("about " if is_money(cost) else "") + figure(cost, lo, hi) + " " + per(unit, cost["period"])


def cost_belief(cost: dict, actor_plural, occasion, role_word) -> str:
    """CommercialChain.costBelief."""
    unit, lo, hi = unit_of(cost, role_word), dec(cost["low"]), dec(cost["high"])
    if cost["mode"] == "RATE":
        of = base_of(cost, occasion)
        return ("Most " + (actor_plural.strip() if actor_plural else "people") + " lose about " + figure(cost, lo, hi)
                + ("" if of is None else " of " + of) + " " + per(unit, cost["period"]) + ".")
    if cost["mode"] == "HOURS":
        rate = dec(cost.get("rate"))
        money = None if rate is None else _range(cmoney(lo * rate, cost.get("currency")),
                                                 cmoney(hi * rate, cost.get("currency")), lo * rate, hi * rate)
        return ("The problem already costs the payer " + figure(cost, lo, hi) + " " + per(unit, cost["period"])
                + ("" if money is None else ", about " + money) + ".")
    return "The problem already costs the payer about " + figure(cost, lo, hi) + " " + per(unit, cost["period"]) + "."


def price_figure(price: dict, lo, hi) -> str:
    if price.get("shape") == "SHARE":
        return _range(cnumber(lo) + "%", cnumber(hi) + "%", lo, hi)
    return _range(cmoney(lo, price.get("currency")), cmoney(hi, price.get("currency")), lo, hi)


def recovered(price: dict) -> bool:
    return price.get("shape") == "SHARE" and price.get("shareBase") == "RECOVERED"


def once(price: dict) -> bool:
    return price.get("shape") == "UPFRONT_THEN" and price.get("thenNothing") is True


def two_steps(price: dict) -> bool:
    """Up front, then a plan: two ladders, a pick `[<one-off>, <plan>]` (115 judgement call 8)."""
    return price.get("shape") == "UPFRONT_THEN" and not once(price)


def price_said(price: dict, cost, occasion, role_word):
    """CommercialChain.priceSaid (the period is the cost's)."""
    unit, period = unit_of(cost, role_word), (cost or {}).get("period")
    shape = price.get("shape")
    if shape == "FREE":
        return None
    if shape == "SHARE":
        of = "of what it gets back, only when it does" if recovered(price) else (
            "" if base_of(cost, occasion) is None else "of " + base_of(cost, occasion))
        return (price_figure(price, dec(price["low"]), dec(price["high"]))
                + ("" if not of else " " + of + ("," if recovered(price) else "")) + " " + per(unit, period))
    if shape == "UPFRONT_THEN":
        up = price_figure(price, dec(price["upfrontLow"]), dec(price["upfrontHigh"])) + " up front"
        return up + ", then nothing" if once(price) else (
            up + ", then " + price_figure(price, dec(price["low"]), dec(price["high"])) + " " + per(unit, period))
    return price_figure(price, dec(price["low"]), dec(price["high"])) + " " + per(unit, period)


def free_line(actor_plural, decider) -> str:
    return "Free to " + (actor_plural.strip() if actor_plural else "them") + "; paid by " + (
        the(decider) if decider else "someone else")


def price_belief(price: dict, cost, actor_plural, occasion, role_word, decider) -> str:
    if price.get("shape") == "FREE":
        return free_line(actor_plural, decider) + "."
    return "The payer would think it worth " + price_said(price, cost, occasion, role_word) + "."


def reading(cost, price):
    """CommercialChain.reading (115 FR-6): compare, out_of_gain, from_what_comes_back, free or budget."""
    if price is None:
        return None
    if price.get("shape") == "FREE":
        return "free"
    if recovered(price):
        return "from_what_comes_back"
    if cost is None:
        return "budget"
    if price.get("shape") == "SHARE":
        return "out_of_gain" if is_percent(cost) else "budget"
    plan_amount = price.get("shape") != "UPFRONT_THEN" or not once(price)
    return "compare" if is_money(cost) and plan_amount else "budget"


def derive(cost, price) -> dict:
    """CommercialChain.derive: the reading as the band; the ratio only where the founder's own numbers compare."""
    read = reading(cost, price)
    lo = hi = None
    if read in ("compare", "out_of_gain") and dec(cost["low"]) > 0 and price.get("low") is not None:
        lo = int((dec(price["low"]) * 100 / dec(cost["high"])).quantize(D(1), ROUND_HALF_UP))
        hi = int((dec(price["high"]) * 100 / dec(cost["low"])).quantize(D(1), ROUND_HALF_UP))
    return {"ratio_low": lo, "ratio_high": hi, "band": read}


def ability_belief(derived: dict, actor_plural, decider) -> str:
    """CommercialChain.abilityBelief."""
    lo, hi = derived.get("ratio_low"), derived.get("ratio_high")
    ratio = None if lo is None else (f"{lo}%" if lo == hi else f"{lo}% to {hi}%")
    band = derived.get("band")
    if band == "out_of_gain":
        return "Your price is paid out of the gain" + ("" if ratio is None else ": " + ratio + " of what they lose") + "."
    if band == "compare":
        return ("Your price is read against what the problem costs them today"
                + ("" if ratio is None else ": " + ratio + " of it") + ".")
    if band == "from_what_comes_back":
        return "Your price is paid only from what comes back."
    if band == "free":
        return free_line(actor_plural, decider) + "."
    return "Your price is read against where the money would come from."


def ability_phrase(derived: dict, actor_plural, decider) -> str:
    s = ability_belief(derived, actor_plural, decider)
    s = s[:-1] if s.endswith(".") else s
    return s[:1].lower() + s[1:]


def _with_founder(low, percent: bool) -> list:
    points = list(PERCENT_POINTS if percent else MONEY_POINTS)
    if any(p == low for p in points):
        return points
    nearest, best = 0, float("inf")
    for i, p in enumerate(points):
        r = abs(math.log(float(p) / float(low)))
        if r < best:
            best, nearest = r, i
    points[nearest] = D(low).normalize()
    return points


def bands(low, percent: bool, prefix: str = "") -> list:
    """CommercialChain.bands: the six rungs around the founder's low, as `(code, low edge, high edge)` -- 1-2-5 points,
    the point nearest the founder's low giving way to it (115 judgement call 6), then `would_not_pay`."""
    low = D(str(low))
    points = _with_founder(low, percent)
    f = max(i for i, p in enumerate(points) if p == low)
    k = max(0, min(f - 1, len(points) - 4))
    out = [(f"{prefix}under_{plain(points[k])}", None, points[k])]
    for i in range(k, k + 3):
        out.append((f"{prefix}band_{plain(points[i])}_{plain(points[i + 1])}", points[i], points[i + 1]))
    out.append((f"{prefix}over_{plain(points[k + 3])}", points[k + 3], None))
    out.append((f"{prefix}{WOULD_NOT_PAY}", None, None))
    return out


def codes(price: dict) -> list:
    """The ladder codes a chain price is served with: one ladder, or on UPFRONT_THEN the thing's six then the plan's
    six; FREE asks no price item (none)."""
    shape = price.get("shape")
    if shape == "FREE":
        return []
    if shape == "UPFRONT_THEN":
        thing = [c for c, _, _ in bands(price["upfrontLow"], False, UPFRONT)]
        return thing if once(price) else thing + [c for c, _, _ in bands(price["low"], False)]
    return [c for c, _, _ in bands(price["low"], shape == "SHARE")]


def floor_of(code):
    """CommercialChain.floorOf: 0 for under, the low for a band or over, else None (the prefix dropped)."""
    c = str(code)
    c = c[len(UPFRONT):] if c.startswith(UPFRONT) else c
    p = c.split("_")
    return D(0) if p[0] == "under" else dec(p[1]) if p[0] in ("band", "over") and len(p) > 1 else None


def words_fault(field: str, text, required: bool, most: int):
    """VectorCalibration.requireWords: present where required, 1 to `most` words, no digits (lossPhrase may), 120 chars."""
    if not isinstance(text, str) or not text.strip():
        return f"needs its {field} in the founder's own words" if required else None
    count = len(text.split())
    if count > most:
        return f"takes its {field} in at most {most} words; '{text}' has {count}"
    if field != "lossPhrase" and re.search(r"\d", text):
        return f"takes its {field} in words with no digits ('{text}')"
    if len(text.strip()) > 120:
        return f"takes its {field} in at most 120 characters"
    return None


def equation_words(cost: dict, occasion=None, role_word=None) -> str:
    """keel-web 094's equation read back, as keel-cloud words it: the phrase the cost's belief carries (`costSaid`) --
    what the harness holds the founder's drawn equation line against."""
    return cost_said(cost, occasion, role_word)


def locked_words(cost: dict, occasion=None, role_word=None) -> dict:
    """The price's locked words (`CalibrationQuestion.price.locked`, keel-cloud 115 FR-3): the cost's base, unit and
    period -- `CommercialChain.baseOf` / `unitOf` -- which every chain price takes and never sends."""
    return {"base": base_of(cost, occasion), "unit": unit_of(cost, role_word), "period": cost.get("period")}
