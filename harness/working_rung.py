"""keel-cloud 203's `WorkingRung`, restated: whether a Current solution rung's words say today's way fell short.

Spec 203 (the founder, 2026-11-03 08:15 ET, on an angel-group screening study: *"all of them are against their current
solution ... there's nothing which supports their current way of working"*): the scale opens on the outcome where
today's way got the job done, and the line sits under at least one such rung. Code reads a rung as a shortfall by a
short, closed vocabulary -- the founder's own examples and the registry's shortfall words for the row -- unless the word
before it negates it (*Nothing fell short*, *Never failed*). Never a trade's words.

Read by the scripted founder-lists writer (`harness/vectors_script.keels_working_first`, `founder_rungs`), by the
dimension card's test (`tests/test_dimension_cards_131.py`: the card's vocabulary is this one, and keel-cloud's) and by
the scripted reader's R7 on a Current solution scale (spec 131 FR-6).

Spec 161 (keel-cloud 269 FR-5): Current solution left the PROBLEM study -- these rules read only a stored scale now.
Frequency's five rows take its place on the ladder: `frequency_side` reads a pick held (A, B) or against (C, D, E).
"""

from __future__ import annotations

import re

#: `WorkingRung.SHORTFALL`, whole words, case aside.
SHORTFALL = re.compile(r"\b(inconsistent(?:ly)?|uneven(?:ly)?|unsupported|too weak|never enough|not enough"
                       r"|fail(?:s|ed|ing|ures?)?|f[ae]ll(?:s|ing)? short|not good enough"
                       r"|didn['’]t work|did not work|never worked|doesn['’]t work|cost them money)\b", re.I)
#: `WorkingRung.NEGATIONS`: a word before a shortfall word that negates it.
NEGATIONS = frozenset({"nothing", "no", "none", "never", "without", "nobody"})
_WORD_BEFORE = re.compile(r"([^\W\d_]+)\W*$")


def shortfall(rung: str | None) -> str | None:
    """`WorkingRung.shortfall`: the shortfall words a rung says (*inconsistent*), lower-cased, or None."""
    if not rung or not str(rung).strip():
        return None
    for match in SHORTFALL.finditer(str(rung)):
        before = _WORD_BEFORE.search(str(rung)[:match.start()])
        if before and before.group(1).lower() in NEGATIONS:
            continue
        return match.group(1).lower()
    return None


def works(rung: str | None) -> bool:
    """`WorkingRung.works`: the rung reads as today's way working -- it says no shortfall."""
    return shortfall(rung) is None


def working(rungs: list[str], above: int) -> int:
    """`WorkingRung.working`: how many of the first `above` rungs, from the top, read as working before the first
    shortfall -- 0 where the first rung is one (a scale where nothing works)."""
    most = min(max(above, 0), len(rungs))
    n = 0
    while n < most and works(rungs[n]):
        n += 1
    return n


# ----------------------------------------------------------------------------------- spec 161: Frequency's five rows

#: Spec 161 FR-6 (keel-cloud 269 FR-3, 270 FR-2): each Frequency pick's place for the ladder -- *Every time* (A) and
#: *Most times* (B) hold for the founder; *About half the time* (C), *Now and then* (D) and *Never* (E) are against
#: (Never after a yes is owed the second stem; About half and Now and then the rung's own why).
FREQUENCY_FOR = ("every_time", "most_times")
FREQUENCY_AGAINST = ("about_half", "now_and_then", "never")
FREQUENCY_LETTERS = {"A": "every_time", "B": "most_times", "C": "about_half", "D": "now_and_then", "E": "never"}


def frequency_side(code: str | None) -> str | None:
    """`held` for A and B, `against` for C, D and E, None for anything else (a chip, nothing said)."""
    code = FREQUENCY_LETTERS.get(str(code or "").upper(), code)
    if code in FREQUENCY_FOR:
        return "held"
    if code in FREQUENCY_AGAINST:
        return "against"
    return None
