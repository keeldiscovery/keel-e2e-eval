"""S-016: money alone (spec 071 FR-3; keel-cloud 133, keel-web 109), on both of its links (spec 100; keel-cloud 166,
keel-web 145).

**B2B, short** -- 01-countly with the restaurant owner deciding (`evals/scope_journey.money_entry`), as money alone: the
choose screen's money card, Context with no recall window, the problem chat, the idea card (*Your idea*), who decides,
the money calibration, the lock; **only the decision-maker's link** is issued, one an owner; each opens with the problem
in one spoken sentence, the idea card, then part 3 (no gate). The Overview reads *Will they pay?*, the Pilot and *What
they would pay* tiles, one card, a one-piece ship; the decision by the rule.

**Consumer** (spec 100) -- 01-countly on its own persona (`evals/scope_journey.consumer_money_entry`): every person on
the one FULL link, which serves no gate and asks the screener (`Interview.condition`, *Do you run one or two sites?*)
before the idea card; Countly's ten answer it inside and go on through the reveal and the six money questions (their
body the answers alone, spec 102); one more (`OUTSIDE_PERSON`) answers it outside, sends `{outsideSegment: true}` alone
and meets the exit, counted apart on the wire, the People rows and Sent's mark. SC1-SC8 (`evals/scope_marks.py`).
"""

from __future__ import annotations

from evals import scope_journey


def test_s016_money_only(stack, founder_one, browser, run_dir):
    scope_journey.run(stack, founder_one, browser, run_dir, scope="COMMERCIAL", entry_from=scope_journey.money_entry,
                      slug="s016-money-only")


def test_s016_money_only_consumer(stack, founder_one, browser, run_dir):
    scope_journey.run(stack, founder_one, browser, run_dir, scope="COMMERCIAL",
                      entry_from=scope_journey.consumer_money_entry, slug="s016-money-consumer")
