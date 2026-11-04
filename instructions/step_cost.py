"""Spec 133 FR-1 / FR-2 (keel-cloud 211 FR-6, `domain.vectors.StepCost`; rule `L34`), a read-only port.

Whether Commitment's step costs the person something -- spec 205's (and 118's) definition: **money** (an amount, or a
price, fee, deposit, pre-order, paid pilot or moved funds, even with money back or free returns), **data** (letting the
founder's side read, run on or collect from their records, systems or activity) or **a signature** (a contract, a
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


@dataclass(frozen=True)
class Cost:
    """`StepCost.Cost`: what the step costs and the word that says so."""
    kind: str
    word: str


def of(step: str | None) -> Cost | None:
    """`StepCost.of`: the step's cost, or None where it costs nothing the engine can read -- an amount first
    (`Wording.money`), then a money word, a signature word, a data word."""
    if step is None or not str(step).strip():
        return None
    amount = wording_mod.money(step)
    if amount:
        return Cost(MONEY, amount)
    text = str(step).lower().replace("in order to", "")
    for kind, pattern in ((MONEY, MONEY_WORDS), (SIGNATURE, SIGNATURE_WORDS), (DATA, DATA_WORDS)):
        found = pattern.search(text)
        if found:
            return Cost(kind, found.group(1))
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
