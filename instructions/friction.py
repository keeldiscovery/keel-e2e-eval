"""Purchase friction measured in time (spec 118 FR-2; keel-cloud 182, `PurchaseFriction`), a read-only port.

keel-cloud 182 asks the founder how long the picked step takes (`SavedList.duration {count, unit}`, DAYS | WEEKS |
MONTHS, 1 to 99) and serves the stranger six chips around it (`duration_bands`): five duration bands with one edge
exactly at the founder's time -- the points 1 day, 3 days, 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year, 2 years,
the one nearest the founder's time (on the ratio scale) giving way to it, the band below it *to under* it -- then *It
wouldn't be needed*. A band at or under the founder's time and *It wouldn't be needed* count FOR (`within`), a band from
it AGAINST (`longer`). A list saved before 182 names no time and keeps the fixed three (`UNDATED_CODES`), *a long time*
the one answer against.

Nothing here is the eval's own: every function restates `PurchaseFriction` (keel-cloud-docs `f3f0d99e`), pinned by
`tests/test_money_cards_redrawn_118.py` on 182's own table (`PurchaseFrictionLadderTest`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

UNITS = ("DAYS", "WEEKS", "MONTHS")
MIN_COUNT, MAX_COUNT = 1, 99
NOT_NEEDED = "not_needed"
NOT_NEEDED_LABEL = "It wouldn't be needed"
BAND_PREFIX = "days_"
LONG = "yes_long"
#: A list saved before 182: the fixed three, in order (`ItemFrames.PURCHASE_LABELS`).
UNDATED_CODES = (LONG, "yes_quick", NOT_NEEDED)
#: keel-cloud 182 FR-1 (registry `belief_template`, `PurchaseFriction.UNDATED_BELIEF`).
BELIEF_TEMPLATE = "Most {deciders} would get through {value} within about {duration}, or not need it."
UNDATED_BELIEF = "Most {deciders} would get through {value} quickly, or not need it."
#: keel-cloud 182 FR-3 (`PurchaseFriction.BAR`, `BAR_UNDATED`): the card's bar, after *Keel's bar: *.
BAR = "holds if no more than 1 in 3 say it would take longer than you expect"
BAR_UNDATED = "holds if no more than 1 in 3 say it would take a long time"
#: keel-cloud 182 FR-5: the one follow-up, asked of a band above the founder's time alone (no second stem).
FOLLOW_UP_HEADING = "What would take the time?"
FOLLOW_UP = "What would take the time in buying {solution_name}?"

_MULTIPLIER = {"DAYS": 1, "WEEKS": 7, "MONTHS": 30}
_UNIT_WORD = {"DAYS": "day", "WEEKS": "week", "MONTHS": "month"}


def _word(singular: str, count: int) -> str:
    return singular if count == 1 else singular + "s"


@dataclass(frozen=True)
class Duration:
    """`PurchaseFriction.Duration`: `count` of `unit`."""
    count: int
    unit: str

    @classmethod
    def of(cls, raw) -> "Duration | None":
        """The founder's `{count, unit}` as the entry (or the wire) carries it; None where there is none."""
        if not isinstance(raw, dict) or raw.get("count") is None or not raw.get("unit"):
            return None
        return cls(int(raw["count"]), str(raw["unit"]).strip().upper())

    def valid(self) -> bool:
        return MIN_COUNT <= self.count <= MAX_COUNT and self.unit in UNITS

    def days(self) -> int:
        return self.count * _MULTIPLIER.get(self.unit, 1)

    def said(self) -> str:
        """*6 weeks*, *1 month*, *3 days*."""
        return f"{self.count} {_word(_UNIT_WORD.get(self.unit, 'day'), self.count)}"

    def as_wire(self) -> dict:
        return {"count": self.count, "unit": self.unit}


@dataclass(frozen=True)
class _Point:
    days: int
    count: int
    unit: str

    def said(self) -> str:
        return f"{self.count} {_word(self.unit, self.count)}"


POINTS = (_Point(1, 1, "day"), _Point(3, 3, "day"), _Point(7, 1, "week"), _Point(14, 2, "week"),
          _Point(30, 1, "month"), _Point(90, 3, "month"), _Point(180, 6, "month"), _Point(365, 1, "year"),
          _Point(730, 2, "year"))


def _with_founder(founder: Duration) -> list:
    points = list(POINTS)
    days = founder.days()
    nearest, best = 0, float("inf")
    for i, p in enumerate(points):
        ratio = abs(math.log(p.days / days))
        if ratio < best:
            best, nearest = ratio, i
    points[nearest] = _Point(days, founder.count, _UNIT_WORD.get(founder.unit, "day"))
    return points


def _between(a: _Point, b: _Point, to_under: bool) -> str:
    to = " to under " if to_under else " to "
    return f"{a.count}{to}{b.said()}" if a.unit == b.unit else f"{a.said()}{to}{b.said()}"


def bands(founder: Duration) -> list:
    """`PurchaseFriction.bands`: the six chips as `(code, low days, high days, label)`."""
    if founder is None or not founder.valid():
        raise ValueError(f"a founder's figure of {founder!r} is not a count of days, weeks or months")
    points = _with_founder(founder)
    f = max(i for i, p in enumerate(points) if p.days == founder.days())
    k = max(0, min(f - 1, len(points) - 4))
    first = points[k]
    out = [(f"{BAND_PREFIX}under_{first.days}", None, first.days, f"Under {first.said()}")]
    for i in range(k, k + 3):
        a, b = points[i], points[i + 1]
        out.append((f"{BAND_PREFIX}{a.days}_to_{b.days}", a.days, b.days, _between(a, b, b.days == founder.days())))
    last = points[k + 3]
    out.append((f"{BAND_PREFIX}over_{last.days}", last.days, None, f"Over {last.said()}"))
    out.append((NOT_NEEDED, None, None, NOT_NEEDED_LABEL))
    return out


def codes(founder: Duration) -> list:
    return [b[0] for b in bands(founder)]


def labels(founder: Duration) -> dict:
    return {b[0]: b[3] for b in bands(founder)}


def bounds(code):
    """A band's `(low, high)` in days from its code (None where open); None on any other code."""
    if not isinstance(code, str) or not code.startswith(BAND_PREFIX):
        return None
    rest = code[len(BAND_PREFIX):]
    try:
        if rest.startswith("under_"):
            return None, int(rest[len("under_"):])
        if rest.startswith("over_"):
            return int(rest[len("over_"):]), None
        low, _, high = rest.partition("_to_")
        return int(low), int(high)
    except ValueError:
        return None


def within(code, founder: Duration | None) -> bool:
    """`PurchaseFriction.within`: FOR -- a band at or under the founder's time, or *It wouldn't be needed*; with no time,
    *quick* or *not needed*."""
    if code == NOT_NEEDED:
        return True
    if founder is None:
        return code == "yes_quick"
    b = bounds(code)
    return b is not None and b[1] is not None and b[1] <= founder.days()


def longer(code, founder: Duration | None) -> bool:
    """`PurchaseFriction.longer`: AGAINST -- a band from the founder's time on; with no time, *a long time*."""
    if founder is None:
        return code == LONG
    b = bounds(code)
    return b is not None and b[0] is not None and b[0] >= founder.days()


def belief(deciders: str | None, step: str, founder: Duration | None) -> str:
    """`PurchaseFriction.belief`: *Most {deciders} would get through {step} within about {duration}, or not need it.*;
    *Most would ...* with no decider word; *... quickly, or not need it.* with no time."""
    def lower(text: str) -> str:
        return text if len(text) > 1 and text[1].isupper() else text[:1].lower() + text[1:]

    who = lower(deciders.strip()) if deciders and deciders.strip() else None
    sentence = UNDATED_BELIEF if founder is None else BELIEF_TEMPLATE
    sentence = sentence.replace("Most {deciders} ", "Most ") if who is None else sentence.replace("{deciders}", who)
    value = str(step or "").strip()
    while value.endswith("."):
        value = value[:-1].strip()
    sentence = sentence.replace("{value}", lower(value))
    return sentence if founder is None else sentence.replace("{duration}", founder.said())
