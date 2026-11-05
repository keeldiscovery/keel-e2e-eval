"""Spec 133 FR-1 / FR-2 (keel-cloud 211 FR-6, `domain.vectors.StepCost`; rule `L34`), a read-only port.

Whether Commitment's step costs the person something -- spec 205's (and 118's) definition: **money** (an amount, or a
price, fee, deposit, pre-order, paid pilot or moved funds, even with money back or free returns), **data** (letting the
founder's side read, run on or collect from their records, systems or activity; keel-cloud 221: installing anything of
theirs, or letting it read or measure them, free or not) or **a signature** (a contract, a
letter of intent). A closed vocabulary of the engine's own, no trade's word: code's reading of the step's words, never a
judgement of the offer. A step that costs nothing (a read-only look, a demo, a call, *sample data*, *sign up*) reads
none. Every pattern is the cloud's (keel-cloud-docs `e485abeb`), compiled ASCII as Java's `\\b` reads ASCII text;
`tests/test_cloud_211_mirror_133.py` holds them to the cloud's source.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import wording as wording_mod

MONEY = "money"
DATA = "data"
SIGNATURE = "a signature"

MONEY_WORDS = re.compile(r"(?i)\b(pay|pays|paying|paid|buy|buys|buying|purchase|purchases|purchasing|pre-order|"
                         r"preorder|pre-orders|order|orders|ordering|deposit|deposits|subscribe|subscribes|subscription|"
                         r"fee|fees|invest|invests|fund|funds|licence|license)\b", re.ASCII)
#: Data -- never a demo's own (*a demo on sample data* costs the person nothing).
DATA_WORDS = re.compile(r"(?i)(?<!sample )(?<!demo )(?<!test )(?<!example )(?<!dummy )\b(data|records|recordings|"
                        r"access)\b", re.ASCII)
SIGNATURE_WORDS = re.compile(r"(?i)\b(sign(?!\s+up\b)|signs(?!\s+up\b)|signing(?!\s+up\b)|signed(?!\s+up\b)|contract|"
                             r"contracts|agreement|letter of intent|loi)\b", re.ASCII)
#: keel-cloud 221 FR-3 (`StepCost.DATA_ACTS`; cycle 14, Expanse's *let Expanse measure cluster waste free for two
#: weeks* read as costing nothing): data is also what the founder's side does on the person's systems or to them, free
#: or not -- installing, integrating or uploading anything, handing anything over, or letting it read, measure, monitor,
#: track, scan, access, record, run on, connect to or analyse them. *allow it to use the microphone* is none of them.
DATA_ACTS = re.compile(r"(?i)\b(install|installs|installing|installed|integrate|integrates|integrating|integrated|upload|"
                       r"uploads|uploading|uploaded)\b|\b(?:hand|hands|handing|handed)\s+(?:\S+\s+){0,3}?(over)\b|"
                       r"\b(?:let|lets|letting|allow|allows|allowing)\s+(?:\S+\s+){1,3}?(?:to\s+)?(read|measure|monitor|"
                       r"track|scan|access|record|run|connect|analyse|analyze)\b", re.ASCII)
#: keel-cloud 213 FR-8 (`CommercialChain.MONEY_NOUNS`): money's own words and the currencies' names, no trade's.
MONEY_NOUNS = frozenset({
    "money", "cash", "balance", "balances", "revenue", "revenues", "sales", "turnover", "income", "earnings",
    "collections", "payments", "deposits", "savings", "funds", "reserve", "reserves", "capital", "assets", "budget",
    "budgets", "spend", "spending", "payroll", "fees", "premium", "premiums", "invoices", "billings", "takings", "profit",
    "profits", "wages", "salaries", "dollar", "dollars", "euro", "euros", "pound", "pounds", "rupee", "rupees", "yen",
    "yuan", "franc", "francs", "peso", "pesos", "rand", "krona", "kronor", "krone", "kroner", "lira", "shekel", "shekels",
    "dirham", "dirhams", "ringgit", "baht", "naira", "shilling", "shillings", "rupiah", "zloty", "ruble", "rubles",
    "rouble", "roubles", "dinar", "dinars", "riyal", "riyals", "taka", "reais"})
#: keel-cloud 213 FR-8 (`StepCost.MOVE_WORDS`; cycle 11, Palus' *move a small part of the reserve*): moved funds are
#: money -- a verb that moves a thing and, after it, one of the money nouns.
MOVE_WORDS = re.compile(r"(?i)\b(move|moves|moving|moved|transfer|transfers|transferring|transferred|put|puts|putting|"
                        r"shift|shifts|shifting|shifted|switch|switches|switching|switched|park|parks|parking|parked)\b"
                        r"(.*)$", re.ASCII)
#: keel-cloud 213 FR-8 (`StepCost.DESTINATION`): where the moved money goes -- a destination after the verb.
DESTINATION = re.compile(r"(?i)\b(?:into|to|onto|in|with|at)\s+\S", re.ASCII)


@dataclass(frozen=True)
class Cost:
    """`StepCost.Cost`: what the step costs and the word that says so."""
    kind: str
    word: str


def moved(step: str | None) -> str | None:
    """keel-cloud 213 FR-8 (`StepCost.moved`): the moving verb (lowered) where it carries a money noun after it, else
    None."""
    if step is None:
        return None
    move = MOVE_WORDS.search(str(step))
    if move is None:
        return None
    for word in re.split(r"[^a-z'-]+", move.group(2).lower()):
        if re.sub(r"'s$", "", word) in MONEY_NOUNS:
            return move.group(1).lower()
    return None


def moves_money_nowhere(step: str | None) -> bool:
    """keel-cloud 213 FR-8 (`StepCost.movesMoneyNowhere`): the step moves the person's money and names no place it goes
    (*move a small part of the reserve*) -- the Check row's note asks the founder to say where, never a rewrite."""
    if step is None or not str(step).strip() or moved(step) is None:
        return False
    move = MOVE_WORDS.search(str(step))
    return move is not None and DESTINATION.search(move.group(2)) is None


def of(step: str | None) -> Cost | None:
    """`StepCost.of`: the step's cost, or None where it costs nothing the engine can read -- an amount first
    (`Wording.money`), then a money word, moved money (keel-cloud 213 FR-8), a signature word, a data word, a data act
    (keel-cloud 221 FR-3)."""
    if step is None or not str(step).strip():
        return None
    amount = wording_mod.money(step)
    if amount:
        return Cost(MONEY, amount)
    text = str(step).lower().replace("in order to", "")
    found = MONEY_WORDS.search(text)
    if found:
        return Cost(MONEY, found.group(1))
    verb = moved(text)
    if verb is not None:
        return Cost(MONEY, verb)
    for kind, pattern in ((SIGNATURE, SIGNATURE_WORDS), (DATA, DATA_WORDS)):
        found = pattern.search(text)
        if found:
            return Cost(kind, found.group(1))
    acts = DATA_ACTS.search(text)
    if acts:
        return Cost(DATA, acts.group(1) or acts.group(2) or acts.group(3))
    return None


def costs(step: str | None) -> bool:
    """`StepCost.costs`: whether the step costs the person money, data or a signature."""
    return of(step) is not None


def l34(rows: list[str]) -> str | None:
    """keel-cloud 211 FR-6 (`ScreenResultApplier.l34`): Commitment's list -- the step first, then the smaller step --
    where the step costs the person money, data or a signature and no free smaller step follows it (none, or one that
    costs something itself): the fault in the cloud's words, else None. One repair turn, then a note."""
    if not rows:
        return None
    step = rows[0]
    cost = of(step)
    if cost is None:
        return None
    if len(rows) < 2:
        return (f"L34: '{step}' costs the person {cost.kind} ('{cost.word}'); a step that costs money, data or a "
                "signature takes a second item, the obvious smaller step that costs nothing and comes first, naming "
                "the same product -- a list of one is incomplete")
    its = of(rows[1])
    if its is not None:
        return (f"L34: '{rows[1]}' costs the person {its.kind} ('{its.word}') itself; the smaller step before "
                f"'{step}' costs nothing")
    return None
