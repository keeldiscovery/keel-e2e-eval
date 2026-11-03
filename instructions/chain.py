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
BUDGET_SUPPORTS = ("from_spend", "existing_line", "charged_to_users", "taken_from_other_spend")  # + keel-cloud 198 FR-5
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


#: keel-cloud 145 FR-2 (`BeliefSentence.ACRONYM`): an all-caps token of two to four letters (CEO, CFO, HR, IT) is an
#: acronym, which takes *the* -- never a person's name.
ACRONYM = re.compile(r"^[A-Z]{2,4}s?$")
_ROLE_LEADS = ("the ", "a ", "an ", "their ", "your ", "my ")


def _lower_first(label: str) -> str:
    """`BeliefSentence.lower`: the first letter lowered unless the second is a capital (an acronym)."""
    return label if len(label) > 1 and label[1].isupper() else label[:1].lower() + label[1:]


def _a_name(role: str) -> bool:
    """`BeliefSentence.name` (keel-cloud 145 FR-2): capitalised, its first word no acronym, its second letter lower."""
    first = role.split()[0] if role.split() else ""
    return len(role) > 1 and role[0].isupper() and not ACRONYM.match(first) and not role[1].isupper()


def the_role(role: str) -> str:
    """keel-cloud 145 FR-2 (`BeliefSentence.theRole`): the role with its *the* -- *the CEO*, *the HR director*, *the
    restaurant owner* -- an article of its own lower-cased (*The CFO* -> *the CFO*), a person's name (every word
    capitalised: *Priya*) kept bare. What the four buyer frames, the labels, the belief and the brief's line use."""
    stripped = str(role or "").strip()
    if stripped.lower().startswith(_ROLE_LEADS):
        return _lower_first(stripped)
    if _a_name(stripped) and all(w[:1].isupper() for w in stripped.split()):
        return stripped
    lowered = _lower_first(stripped)
    return _lower_first(lowered if _a_name(lowered) else "the " + lowered)


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


def unit_beside(unit, base, period):
    """keel-cloud 199 FR-10 (`CommercialChain.unitBeside`): the founder's unit, or None where the base already names it
    (the unit's word, or its plural or possessive, in the base), so the sentence says it once -- *the cluster's GPU hours
    a month*, never *... per cluster a month*. A unit of two words or more, and a cost *each* time, keep their unit."""
    if not unit or not str(unit).strip() or not base or not str(base).strip() or " " in str(unit).strip() \
            or period == "each":
        return unit
    pattern = r"(?i)\b" + re.escape(str(unit).strip()) + r"(?:'s|s|es)?\b"
    return None if re.search(pattern, str(base)) else unit


def cost_said(cost: dict, occasion, role_word) -> str:
    """CommercialChain.costSaid: the phrase the drift clause quotes (the belief phrase). Since keel-cloud 199 FR-10 a
    rate's unit is dropped where its base names it (`unit_beside`)."""
    unit, lo, hi = unit_of(cost, role_word), dec(cost["low"]), dec(cost["high"])
    if cost["mode"] == "RATE":
        of = base_of(cost, occasion)
        unit = unit_beside(unit, of, cost["period"])
        return "about " + figure(cost, lo, hi) + ("" if of is None else " of " + of) + " " + per(unit, cost["period"])
    return ("about " if is_money(cost) else "") + figure(cost, lo, hi) + " " + per(unit, cost["period"])


# ------------------------------------------------- spec 118 FR-1 (keel-cloud 180 FR-2, 181 FR-4): who pays, in words

def plural_of(role: str) -> str:
    """keel-cloud `PersonaModel.pluralOf`: *payroll manager* -> *payroll managers*, lower-cased; a plural kept."""
    lower = str(role).lower()
    if lower.endswith("s"):
        return lower
    if lower.endswith("y") and not lower.endswith(("ay", "ey", "oy")):
        return lower[:-1] + "ies"
    return lower + "s"


def plural_words(words: str) -> str:
    """keel-cloud `PersonaModel.pluralWords` (spec 123 FR-10): a title's plural with its case kept -- *Contractor
    operations lead* -> *Contractor operations leads*, *CFO* -> *CFOs*, *head of finance* -> *heads of finance*."""
    text = str(words).strip()
    of = text.lower().find(" of ")
    if of > 0:
        return plural_words(text[:of]) + text[of:]
    space = text.rfind(" ")
    head, last = (text[:space + 1], text[space + 1:]) if space >= 0 else ("", text)
    if len(last) > 1 and last == last.upper():
        return head + last + "s"
    lower = last.lower()
    if lower.endswith("s"):
        return head + last
    if lower.endswith("y") and not lower.endswith(("ay", "ey", "oy")):
        return head + last[:-1] + "ies"
    return head + last + "s"


def deciders(decider_words, actor_plural, b2b: bool):
    """keel-cloud 180 `CommercialChain.deciders(deciderWords, slots, b2b)`: who pays in the founder's word -- the
    decider's title (else role) in the plural where someone else decides, else the people's own plural; None with
    neither. The corpus hands it the decider's `title`, else its `role` (`BacktestCorpusTest.theChainsWordsAreTheEngines`)."""
    if b2b and decider_words and str(decider_words).strip():
        return plural_words(str(decider_words))
    return str(actor_plural).strip() if actor_plural and str(actor_plural).strip() else None


def _upper(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _same_words(a, b) -> bool:
    """`CommercialChain.sameWords` (vectors_script's port): case, articles and person aside, the same words. Spec 125
    FR-1 (keel-cloud 195 FR-2): word by word through `spelling.same_word`, the same count of words -- the founder's loss
    line typed *late shipmnts* is the base *late shipments*; a different word is a different phrase."""
    if a is None or b is None:
        return False
    from harness import loss_line as ll                                # noqa: PLC0415 - the harness's grammar
    from instructions import spelling as spelling_mod                  # noqa: PLC0415

    def norm(t):
        t = ll.second_person(t, False).lower()
        t = re.sub(r"\b(the|a|an)\b", "", t)
        return re.sub(r"[^a-z0-9%]+", " ", t).strip()
    x, y = norm(a), norm(b)
    if x == y:
        return True
    xs, ys = x.split(" "), y.split(" ")
    if not x or not y or len(xs) != len(ys):
        return False
    return all(spelling_mod.same_word(p, q) for p, q in zip(xs, ys))


#: keel-cloud 193 FR-1c (`CommercialChain.LACK`): a base that is the lack itself -- *go without*, *lack*, *miss* --
#: drops *on {base}* on an hours cost (nobody spends time on what they go without).
LACK = re.compile(r"(?i)\b(?:go|goes|went|going) without\b|\black(?:s|ing)?\b|\bmiss(?:es|ed|ing)?\b")

#: keel-cloud 193 FR-1b (`CommercialChain.LOSS_VERBS`): the words a loss phrase opens with when it is a verb phrase the
#: base can carry as its predicate (*carry a dimension error*) -- finite verbs and the auxiliaries only; a noun-led
#: phrase or a participle (*billed as declared*) keeps the colon.
LOSS_VERBS = frozenset({
    "are", "is", "were", "was", "have", "has", "had", "carry", "carries", "get", "gets", "go", "goes", "come", "comes",
    "fail", "fails", "miss", "misses", "need", "needs", "arrive", "arrives", "lack", "lacks", "lose", "loses", "slip",
    "slips", "sit", "sits", "stay", "stays", "end", "wait", "waits", "bounce", "bounces", "never", "can", "cannot",
    "could", "will", "would", "must", "do", "does", "did", "don't", "doesn't", "didn't", "leave", "take", "contain",
    "contains", "include", "includes", "require", "requires", "ship", "cross", "pass", "reach", "sell", "bring", "hold",
    "hit"})

#: keel-cloud `CommercialChain.BASE_ENDS`: the words that end the head of the people's plural (*officers* of *patrol
#: officers at small and mid-sized police departments*).
BASE_ENDS = frozenset({
    "they", "that", "which", "who", "whom", "of", "for", "in", "on", "at", "to", "from", "with", "by", "due", "when",
    "where", "while", "after", "before", "per", "across", "into", "over", "under", "about", "through", "during"})


def loss_predicate(loss) -> bool:
    """keel-cloud 193 FR-1b (`CommercialChain.lossPredicate`): whether the (lowered) loss phrase opens with a verb, so
    the base can carry it as its predicate."""
    if not loss or not str(loss).strip():
        return False
    first = re.sub(r"[^a-z']", "", str(loss).strip().split()[0].lower().replace("\u2019", "'"))
    return first in LOSS_VERBS


def own_noun(unit, actor, actor_plural) -> bool:
    """keel-cloud 193 FR-1a (`CommercialChain.ownNoun`): whether the cost's unit is the subject's own noun -- the actor's
    head word (*officer* of *patrol officer*), or the head of the people's plural (*officers* of *patrol officers at
    small and mid-sized police departments*), singular or plural -- so *per officer* beside patrol officers says the
    people twice."""
    if not unit or not str(unit).strip():
        return False
    u = str(unit).strip().lower()
    a = str(actor or "").strip().lower()
    if a and (a == u or a.endswith(" " + u)):
        return True
    head = None
    for word in re.split(r"[\s,;:]+", str(actor_plural or "").strip().lower()):
        w = re.sub(r"[^a-z-]", "", word)
        if not w:
            continue
        if w in BASE_ENDS:
            break
        head = w
    return head is not None and " " not in u and (head == u or head == plural_of(u))


def cost_belief(cost: dict, occasion, role_word, deciders_words=None, b2b: bool = True, *, actor=None,
                actor_plural=None) -> str:
    """keel-cloud 180 FR-2 (`CommercialChain.costBelief(cost, slots, roleWord, deciders, b2b)`, corpus revision 20):
    the belief names who pays in the founder's word, never *the payer*; *They* with no word; no unit where the user
    pays (`b2b` False); a period of *each* closes its own clause, so the base goes before it.

    Spec 123 FR-1 (keel-cloud 193 FR-1, revision 22 amended in place): the sentence names who really spends --
    **money** is the deciders' (*{Deciders} already spend about {figure} {per} on {base}.*, unchanged); **hours** are
    spent by the context's `actor_plural` (capitalised; *They* with none), the *per {unit}* dropped where the unit is
    their own noun (`own_noun`), and a base that is the lack itself (`LACK`) drops *on {base}*; **a rate with a loss
    phrase** is said of its base, by nobody -- *About {figure} of {base} {per} {loss}.* where the loss opens with a verb
    (`loss_predicate`), else *About {figure} of {base} {per}: {loss}.* (consumer studies too); without a loss phrase,
    *{Actor plural} already lose about {figure} of {base} {per}.* A count whose base names its own measure says the
    number once; the loss line is dropped where it only repeats the base."""
    who = "They" if not deciders_words or not str(deciders_words).strip() else _upper(str(deciders_words).strip())
    actors = "They" if not actor_plural or not str(actor_plural).strip() else _upper(str(actor_plural).strip())
    of = base_of(cost, occasion)
    # keel-cloud 199 FR-10: the base said once -- no *per cluster* after *the cluster's GPU hours*
    unit = unit_beside(unit_of(cost, role_word) if b2b else None, of, cost["period"])
    lo, hi = dec(cost["low"]), dec(cost["high"])
    words = per(unit, cost["period"])
    tail = "" if not words else " " + words
    if cost["mode"] == "RATE":
        loss_text = cost.get("lossPhrase")
        loss = None
        if loss_text and str(loss_text).strip() and not _same_words(loss_text, of):
            loss = str(loss_text).strip()
            while loss.endswith("."):
                loss = loss[:-1].strip()
            loss = _lower_first(loss)
        fig = figure(cost, lo, hi)
        measure = measure_of(cost)
        if of is not None and not is_percent(cost) and measure and re.search(
                r"(?i)\b" + re.escape(measure.strip()) + r"\b", of):
            fig = _range(cnumber(lo), cnumber(hi), lo, hi)
        said = "about " + fig + ("" if of is None else " of " + of) + tail
        if loss is None:
            return actors + " already lose " + said + "."
        return _upper(said) + (" " + loss if loss_predicate(loss) else ": " + loss) + "."
    each = cost.get("period") == "each"
    if cost["mode"] == "HOURS":
        hours_words = per(None if own_noun(unit, actor, actor_plural) else unit, cost["period"])
        hours_tail = "" if not hours_words else " " + hours_words
        on = "" if of is None or LACK.search(of) else " on " + of
        return actors + " already spend " + figure(cost, lo, hi) + (on + hours_tail if each else hours_tail + on) + "."
    on = "" if of is None else " on " + of
    spent = on + tail if each else tail + on
    return who + " already spend about " + figure(cost, lo, hi) + spent + "."


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


def price_belief(price: dict, cost, actor_plural, occasion, role_word, decider, deciders_words=None, name=None,
                 b2b: bool = True) -> str:
    """keel-cloud 180 FR-2 (`CommercialChain.priceBelief(..., deciders, name, b2b)`): *{Deciders} would think {name}
    worth {price}.*; a share *{Deciders} would think a fee of {share} fair for {name}.*; the idea *it* with no name, no
    unit where the user pays; free to them as before (*Free to {actor plural}; paid by {the decider}.*)."""
    if price.get("shape") == "FREE":
        return free_line(actor_plural, decider) + "."
    who = "They" if not deciders_words or not str(deciders_words).strip() else _upper(str(deciders_words).strip())
    idea = "it" if not name or not str(name).strip() else str(name).strip()
    read = cost if b2b else _without_unit(cost)
    said = price_said(price, read, occasion, role_word if b2b else None)
    if price.get("shape") == "SHARE":
        return f"{who} would think a fee of {said} fair for {idea}."
    return f"{who} would think {idea} worth {said}."


def _without_unit(cost):
    """`CommercialChain.withoutUnit`: the cost with no unit (the person who pays is no unit)."""
    return None if cost is None else {**cost, "unit": None}


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


def ability_belief(derived: dict, actor_plural, decider, price=None, cost=None, occasion=None, role_word=None,
                   deciders_words=None, b2b: bool = True) -> str:
    """keel-cloud 181 FR-4 (`CommercialChain.abilityBelief(derived, price, cost, slots, roleWord, deciderRole, deciders,
    b2b)`, corpus revision 20): one sentence per reading over the people who would pay the founder's price, in the
    founder's word for them -- BUDGET *{Deciders} who would pay {price} could find the money for it.* (where the user
    pays *... could find it in money they already spend on this.*); OUT_OF_GAIN *{Deciders} who would pay the {share} fee
    lose at least that much {of base} today, so it is paid out of the gain.*; COMPARE *{Deciders} who would pay {price}
    already lose at least that much to the problem.*; FROM_WHAT_COMES_BACK *... lose something to the problem today, so
    it is paid only from what comes back.*; FREE the founder's own line. Never *Your price is read ...* (spec 141's
    frame), never the ratio. *Those* with no word; *Of {them}, those* where the word carries its own relative clause."""
    band = derived.get("band")
    if band == "free":
        return free_line(actor_plural, decider) + "."
    if not deciders_words or not str(deciders_words).strip():
        who = "Those"
    elif re.search(r"(?i)\b(who|whose|that|which)\b", str(deciders_words)):
        who = "Of " + str(deciders_words).strip() + ", those"
    else:
        who = _upper(str(deciders_words).strip())
    read = cost if b2b else _without_unit(cost)
    if price is None or price.get("shape") == "FREE":
        said = "your price"
    else:
        said = re.sub(r",? (each|then nothing)$", "", price_said(price, read, occasion, role_word if b2b else None),
                      count=1)
    fee = "your fee" if price is None or price.get("shape") != "SHARE" else \
        "the " + price_figure(price, dec(price["low"]), dec(price["high"])) + " fee"
    if band == "out_of_gain":
        of = "" if price is None else _share_of(price, cost, occasion)
        return f"{who} who would pay {fee} lose at least that much" + ("" if not of else " " + of) + \
            " today, so it is paid out of the gain."
    if band == "compare":
        return f"{who} who would pay {said} already lose at least that much to the problem."
    if band == "from_what_comes_back":
        return f"{who} who would pay {fee if price is not None and price.get('shape') == 'SHARE' else said} lose " \
               "something to the problem today, so it is paid only from what comes back."
    return f"{who} who would pay {said} could find the money for it." if b2b else \
        f"{who} who would pay {said} could find it in money they already spend on this."


def _share_of(price: dict, cost, occasion) -> str:
    """`CommercialChain.shareOf`: *of the balance*, or *of what it gets back, only when it does*."""
    if recovered(price):
        return "of what it gets back, only when it does"
    base = base_of(cost, occasion)
    return "" if base is None else "of " + base


def ability_phrase(derived: dict, actor_plural, decider, price=None, cost=None, occasion=None, role_word=None) -> str:
    """keel-cloud 181 FR-4 (`CommercialChain.phrase` on Ability to pay): the belief lowered, its full stop gone -- over
    the decider's ROLE in the plural (`deciders(deciderRole, slots, deciderRole != null)`), not the title the sentence
    reads: Fresco's sentence says *Contractor operations leads*, its phrase *contractors*."""
    b2b = decider is not None
    s = ability_belief(derived, actor_plural, decider, price, cost, occasion, role_word,
                       deciders(decider, actor_plural, b2b), b2b)
    s = s[:-1] if s.endswith(".") else s
    return _lower_first(s)


#: keel-cloud 181 FR-2 (`CommercialChain.POINTS_BACK`): Ability to pay's stored and spoken question on a chain study
#: with a price -- asked only of a Price answer at or above the founder's price (`InterviewItem.askedAfter`).
POINTS_BACK = "Think of the price you just gave. If you went ahead at that, where would the money come from?"
#: keel-cloud 181 FR-2 (T007): its escape on every link, *I can't say* (the decision-maker's *I can't recall one* gone).
POINTS_BACK_ESCAPE = "cant_say"


def asks_back(price) -> bool:
    """Whether Ability to pay points back to the price (`CommercialChain.pointsBack`): a chain price, not free."""
    return price_in_chain(price) and price.get("shape") != "FREE"


def at_or_above(code, low) -> bool:
    """`CommercialChain.atOrAbove`: a band (or *over*) whose low edge is at or above the founder's low on its step."""
    floor = floor_of(code)
    return floor is not None and low is not None and floor >= dec(low) and not str(code).endswith(WOULD_NOT_PAY)


def reached(price: dict, pick) -> bool:
    """keel-cloud 181 FR-1 (`Compare.reach` is REACHED): a person's Price pick at or above the founder's price on each
    step -- on up front then a plan, the one-off's against its own low and the plan's against the price's; any other
    answer (a lower band, *would not pay*, the escape, none) is not reached, and the interview never asks them Ability
    to pay (`askedAfter`)."""
    if not isinstance(price, dict) or pick is None or isinstance(pick, dict):
        return False
    if two_steps(price):
        return isinstance(pick, list) and len(pick) == 2 and at_or_above(pick[0], price.get("upfrontLow")) \
            and at_or_above(pick[1], price.get("low"))
    if isinstance(pick, list):
        pick = pick[0] if len(pick) == 1 else None
    low = price.get("upfrontLow") if price.get("shape") == "UPFRONT_THEN" else price.get("low")
    return isinstance(pick, str) and at_or_above(pick, low)


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
